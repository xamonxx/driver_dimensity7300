#!/usr/bin/env python3
"""xamonxx 0003: on-device diagnostics (active only with -DXAMONXX_DIAG).

Run from the Mesa source root AFTER 0001_frame_pacer.py and 0002_device_profile.py.

Problem: on the owner's phone every driver force-closes "when the game opens", and the
loader cannot set env vars nor show logcat. This makes the driver report by itself:

  <dir> = /sdcard/Android/media/<package>/  (an app may create and write its own media
          dir without any permission, and file managers can open it), else /sdcard/Download.

  <dir>/xamonxx_mali7300_crash.log
      written at load time: driver version, pid, process, kernel, driver base address;
      on SIGSEGV/SIGBUS/SIGILL/SIGFPE/SIGABRT/SIGTRAP: signal, code, fault address,
      PC/LR/SP/FP and their offsets inside the driver, plus a bounded frame-pointer walk.
      The handler only uses async-signal-safe write(); it restores the previous handler
      and lets the fault re-trigger (or re-raises SIGABRT), so the app's own crash
      handling still runs.
  <dir>/xamonxx_mali7300_mesa.log
      Mesa's own log at info level (kbase probe, gpu_id, device creation, errors),
      through the 0002 option table defaults MESA_LOG_FILE / MESA_LOG_LEVEL.
"""
import sys
from pathlib import Path


def must_replace(text, old, new, what, path):
    n = text.count(old)
    if n != 1:
        sys.exit(f"xamonxx diagnostics: anchor '{what}' in {path} found {n}x (expected 1)")
    return text.replace(old, new, 1)


# --------------------------------------------------------------------------- os_misc.c
misc = Path("src/util/os_misc.c")
src = misc.read_text(encoding="utf-8")
if "xamonxx_profile_default" not in src:
    sys.exit("xamonxx diagnostics: apply 0002_device_profile.py first")

if "xamonxx_diag_dir" not in src:
    DIAG_MISC = r'''#ifdef XAMONXX_DIAG
#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

/* Package name from /proc/self/cmdline (Android sets it there, not in __progname). */
static void
xamonxx_diag_package(char *out, size_t size)
{
   int fd = open("/proc/self/cmdline", O_RDONLY | O_CLOEXEC);
   ssize_t n = fd >= 0 ? read(fd, out, size - 1) : -1;

   if (fd >= 0)
      close(fd);
   if (n <= 0) {
      snprintf(out, size, "unknown");
      return;
   }
   out[n] = '\0';
   for (char *p = out; *p; p++) {
      if (*p == ':' || *p == '/') {
         *p = '\0';
         break;
      }
   }
   if (!out[0])
      snprintf(out, size, "unknown");
}

/* Called first from the driver's load-time constructor, so it is set up
 * before any other thread can reach it. */
const char *xamonxx_diag_dir(void);
const char *
xamonxx_diag_dir(void)
{
   static char dir[256];

   if (!dir[0]) {
      char pkg[160];
      xamonxx_diag_package(pkg, sizeof(pkg));
      snprintf(dir, sizeof(dir), "/sdcard/Android/media/%s", pkg);
      mkdir("/sdcard/Android/media", 0775);
      if (mkdir(dir, 0775) != 0 && errno != EEXIST)
         snprintf(dir, sizeof(dir), "/sdcard/Download");
   }
   return dir;
}

static const char *
xamonxx_diag_mesa_log(void)
{
   static char path[320];

   if (!path[0])
      snprintf(path, sizeof(path), "%s/xamonxx_mali7300_mesa.log", xamonxx_diag_dir());
   return path;
}
#endif /* XAMONXX_DIAG */

static const char *
xamonxx_profile_default(const char *name)
{
#ifdef XAMONXX_DIAG
   if (strcmp(name, "MESA_LOG_FILE") == 0)
      return xamonxx_diag_mesa_log();
   if (strcmp(name, "MESA_LOG_LEVEL") == 0)
      return "info";
#endif
'''
    src = must_replace(src, "static const char *\nxamonxx_profile_default(const char *name)\n{\n",
                       DIAG_MISC, "xamonxx_profile_default", misc)
    misc.write_bytes(src.encode("utf-8"))
    print("xamonxx diagnostics: os_misc.c patched")
else:
    print("xamonxx diagnostics: os_misc.c already patched")

# --------------------------------------------------------------------------- panvk_wsi.c
wsi = Path("src/panfrost/vulkan/panvk_wsi.c")
src = wsi.read_text(encoding="utf-8")
if "xamonxx_frame_pace" not in src:
    sys.exit("xamonxx diagnostics: apply 0001_frame_pacer.py first")

if "xamonxx_diag_handler" in src:
    print("xamonxx diagnostics: panvk_wsi.c already patched")
    sys.exit(0)

CRASH = r'''

/* ---- xamonxx mali7300: on-device crash diagnostics ------------------------ */
#ifdef XAMONXX_DIAG
#include <dlfcn.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/utsname.h>
#include <ucontext.h>

const char *xamonxx_diag_dir(void);

static int xamonxx_diag_fd = -1;
static uintptr_t xamonxx_diag_base;
static struct sigaction xamonxx_diag_old[NSIG];
static const int xamonxx_diag_sigs[] = {
   SIGSEGV, SIGBUS, SIGILL, SIGFPE, SIGABRT, SIGTRAP,
};

/* Async-signal-safe output helpers (write() only, no stdio). */
static void
xamonxx_diag_puts(const char *s)
{
   if (xamonxx_diag_fd < 0)
      return;
   size_t n = 0;
   while (s[n])
      n++;
   ssize_t r = write(xamonxx_diag_fd, s, n);
   (void)r;
}

static void
xamonxx_diag_hex(const char *label, uint64_t v)
{
   char buf[24];
   int i = 20;

   buf[21] = '\n';
   buf[22] = '\0';
   do {
      buf[i--] = "0123456789abcdef"[v & 0xf];
      v >>= 4;
   } while (v && i > 1);
   buf[i--] = 'x';
   buf[i] = '0';
   xamonxx_diag_puts(label);
   xamonxx_diag_puts(&buf[i]);
}

static void
xamonxx_diag_addr(const char *label, uint64_t addr)
{
   xamonxx_diag_hex(label, addr);
   if (xamonxx_diag_base && addr >= xamonxx_diag_base &&
       addr - xamonxx_diag_base < (1ull << 30))
      xamonxx_diag_hex("    in libvulkan driver at offset ", addr - xamonxx_diag_base);
}

static void
xamonxx_diag_handler(int sig, siginfo_t *si, void *uctx)
{
   xamonxx_diag_puts("\n=== CRASH ===\n");
   xamonxx_diag_hex("signal ", (uint64_t)sig);
   xamonxx_diag_hex("code   ", (uint64_t)(int64_t)si->si_code);
   xamonxx_diag_hex("fault  ", (uint64_t)(uintptr_t)si->si_addr);
   xamonxx_diag_hex("tid    ", (uint64_t)gettid());
#if defined(__aarch64__)
   const ucontext_t *uc = uctx;
   const uint64_t pc = uc->uc_mcontext.pc;
   const uint64_t lr = uc->uc_mcontext.regs[30];
   const uint64_t sp = uc->uc_mcontext.sp;
   uint64_t fp = uc->uc_mcontext.regs[29];

   xamonxx_diag_addr("pc     ", pc);
   xamonxx_diag_addr("lr     ", lr);
   xamonxx_diag_hex("sp     ", sp);
   xamonxx_diag_hex("fp     ", fp);
   if (xamonxx_diag_fd >= 0)
      fsync(xamonxx_diag_fd);

   /* Frame-pointer walk, bounded and sanity-checked (stays inside the stack). */
   xamonxx_diag_puts("backtrace (fp chain):\n");
   for (int i = 0; i < 24; i++) {
      if (!fp || (fp & 0xf) || fp < sp || fp - sp > (8ull << 20))
         break;
      const uint64_t *frame = (const uint64_t *)(uintptr_t)fp;
      const uint64_t next = frame[0];
      const uint64_t ret = frame[1];
      xamonxx_diag_addr("  #  ", ret);
      if (next <= fp)
         break;
      fp = next;
   }
#else
   (void)uctx;
#endif
   xamonxx_diag_puts("=== END ===\n");
   if (xamonxx_diag_fd >= 0)
      fsync(xamonxx_diag_fd);

   /* Hand the signal back: the previous handler (ART/app) runs when the
    * faulting instruction re-executes; SIGABRT is re-raised. */
   sigaction(sig, &xamonxx_diag_old[sig], NULL);
   if (sig == SIGABRT || si->si_code <= 0)
      raise(sig);
}

__attribute__((constructor)) static void
xamonxx_diag_init(void)
{
   char path[320];
   char line[512];

   snprintf(path, sizeof(path), "%s/xamonxx_mali7300_crash.log", xamonxx_diag_dir());
   xamonxx_diag_fd = open(path, O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);

   Dl_info info;
   const char *lib = "?";
   if (dladdr((void *)xamonxx_diag_init, &info) && info.dli_fbase) {
      xamonxx_diag_base = (uintptr_t)info.dli_fbase;
      lib = info.dli_fname ? info.dli_fname : "?";
   }

   struct utsname un;
   if (uname(&un) != 0)
      memset(&un, 0, sizeof(un));

   snprintf(line, sizeof(line),
            "xamonxx mali7300 diagnostics\n"
            "driver   Mesa " PACKAGE_VERSION MESA_GIT_SHA1 "\n"
            "pid      %d\n"
            "kernel   %s %s\n"
            "library  %s\n"
            "base     0x%" PRIxPTR "\n"
            "fps cap  %d (compiled)\n"
            "status   loaded; a CRASH block below means the driver faulted\n",
            (int)getpid(), un.release, un.machine, lib, xamonxx_diag_base,
            XAMONXX_FPS_CAP);
   xamonxx_diag_puts(line);

   struct sigaction sa;
   memset(&sa, 0, sizeof(sa));
   sa.sa_sigaction = xamonxx_diag_handler;
   sa.sa_flags = SA_SIGINFO | SA_RESTART;
   sigemptyset(&sa.sa_mask);
   for (unsigned i = 0; i < ARRAY_SIZE(xamonxx_diag_sigs); i++)
      sigaction(xamonxx_diag_sigs[i], &sa, &xamonxx_diag_old[xamonxx_diag_sigs[i]]);

   mesa_logi("xamonxx mali7300: diagnostics -> %s", path);
}
#endif /* XAMONXX_DIAG */
'''

src = src.rstrip("\n") + CRASH
wsi.write_bytes(src.encode("utf-8"))
print("xamonxx diagnostics: panvk_wsi.c patched (active with -DXAMONXX_DIAG)")
