#!/usr/bin/env python3
"""xamonxx 0002: compiled-in device profile for Mali-G615 MC2 (Infinix X6857 / MT6878).

Why: loaders such as the GTA V launcher cannot set environment variables, but the
PanVK-kbase fixes this GPU needs are only reachable through options:

  * zenithblue issue #54 (G615 MC2, v26.3.1): the GPU is lost a few minutes in with kbase
    incremental rendering; "PANVK_KBASE_TILER_IR=0 PANVK_KBASE_HEAP_CHUNKS=10,400" fixes it
    (IR is on by default for pan arch v11). With IR off a heap exhaustion is DEVICE_LOST,
    hence the larger heap (10 initial / 400 max chunks), exactly the verified pair.
  * profile 2 ("safe"): additionally falls back to the plain present and sync paths
    (no Android present thread, CPU waits for same-queue semaphores) to isolate
    loader/compat crashes.

How: os_get_option() (src/util/os_misc.c) looks up getenv(), then debug.mesa.* Android
properties. This adds a third, last step: a const table compiled in with
-DXAMONXX_PROFILE=<1|2>. A user-set env var or property still wins. No setenv() at load
time (not thread-safe), no change to any option parser.
"""
import sys
from pathlib import Path

path = Path("src/util/os_misc.c")
src = path.read_text(encoding="utf-8")

if "xamonxx_profile_default" in src:
    print("xamonxx device profile: already applied")
    sys.exit(0)


def must_replace(text, old, new, what):
    n = text.count(old)
    if n != 1:
        sys.exit(f"xamonxx device profile: anchor '{what}' found {n}x (expected 1)")
    return text.replace(old, new, 1)


TABLE = r'''#ifdef XAMONXX_PROFILE
/* xamonxx mali7300: device profile for Mali-G615 MC2 (Infinix X6857, MT6878).
 * Consulted only when neither the environment nor a debug.mesa.* property
 * sets the option, so users can still override every value. */
struct xamonxx_option_default {
   const char *name;
   const char *value;
};

static const struct xamonxx_option_default xamonxx_defaults[] = {
   /* zenithblue#54: G615 MC2 loses the GPU with kbase incremental rendering. */
   { "PANVK_KBASE_TILER_IR", "0" },
   { "PANVK_KBASE_HEAP_CHUNKS", "10,400" },
#if XAMONXX_PROFILE >= 2
   /* Safe profile: plain present and sync paths. */
   { "PANVK_ANDROID_PRESENT_THREAD", "0" },
   { "PANVK_KBASE_GPU_SEMAPHORE_WAITS", "0" },
#endif
};

static const char *
xamonxx_profile_default(const char *name)
{
   for (size_t i = 0; i < sizeof(xamonxx_defaults) / sizeof(xamonxx_defaults[0]); i++) {
      if (strcmp(name, xamonxx_defaults[i].name) == 0)
         return xamonxx_defaults[i].value;
   }
   return NULL;
}
#endif /* XAMONXX_PROFILE */

static const char *
os_get_option_internal(const char *name, bool use_secure_getenv)
{'''

src = must_replace(src,
                   "static const char *\nos_get_option_internal(const char *name, bool use_secure_getenv)\n{",
                   TABLE, "os_get_option_internal (non-Windows)")

old_tail = """#if DETECT_OS_ANDROID
   if (!opt) {
      opt = os_get_android_option_cached(name);
   }
#endif
   return opt;
}"""
new_tail = """#if DETECT_OS_ANDROID
   if (!opt) {
      opt = os_get_android_option_cached(name);
   }
#endif
#ifdef XAMONXX_PROFILE
   if (!opt)
      opt = xamonxx_profile_default(name);
#endif
   return opt;
}"""
src = must_replace(src, old_tail, new_tail, "option lookup tail")

if "#include <string.h>" not in src:
    src = must_replace(src, "#include \"os_misc.h\"\n", "#include \"os_misc.h\"\n#include <string.h>\n",
                       "os_misc.h include")

path.write_bytes(src.encode("utf-8"))
print("xamonxx device profile: applied (active with -DXAMONXX_PROFILE=1|2)")
