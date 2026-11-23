#!/usr/bin/env python3
"""xamonxx 0001: precise frame pacer for PanVK (Mali kbase), target 30/60 fps stable.

Run from the Mesa source root AFTER the zenithblue release series
(needs panvk_QueuePresentKHR / panvk_QueueSignalReleaseImageANDROID from
csf-v11/233 "panvk-fps-log-present-counter").

Where it hooks (both are the only frame-boundary entry points of the driver):
  * panvk_QueuePresentKHR            -> X11 (Winlator/Wine), Wayland and PanVK's own
                                        Android-surface swapchain
  * panvk_QueueSignalReleaseImageANDROID -> Android loader swapchain (native Android apps)
The two paths never call each other, so a frame is paced exactly once.

How it paces:
  * fixed cadence of absolute deadlines on CLOCK_MONOTONIC, slept with
    clock_nanosleep(TIMER_ABSTIME), so there is no busy-wait and no drift;
  * a frame up to one interval late keeps the cadence (no phase jump);
  * a frame later than that re-syncs instead of bursting to catch up;
  * the lock is never held while sleeping.
Result: even frame times. The GPU and CPU idle for the rest of each frame, so the
SoC runs cooler and throttles later, which keeps the FPS stable over long sessions.

Configuration:
  compile time  -DXAMONXX_FPS_CAP=<fps>   (0 = off)
  run time      XAMONXX_FPS_CAP=<fps>     env var / debug.mesa.* property (os_get_option)
                valid 10..240, 0 disables, other values fall back to off.
"""
import sys
from pathlib import Path

path = Path("src/panfrost/vulkan/panvk_wsi.c")
src = path.read_text(encoding="utf-8")

if "xamonxx_frame_pace" in src:
    print("xamonxx frame pacer: already applied")
    sys.exit(0)


def must_replace(text, old, new, what):
    n = text.count(old)
    if n != 1:
        sys.exit(f"xamonxx frame pacer: anchor '{what}' found {n}x (expected 1)")
    return text.replace(old, new, 1)


PACER = r'''/* ---- xamonxx mali7300: precise frame pacer ------------------------------ */
#include <errno.h>

#ifndef XAMONXX_FPS_CAP
#define XAMONXX_FPS_CAP 0
#endif

/* 0 = not read yet, 1 = off, 2 = on. */
static int xamonxx_pace_state;
static uint64_t xamonxx_pace_interval_ns;
static uint64_t xamonxx_pace_next_ns;
static simple_mtx_t xamonxx_pace_lock = SIMPLE_MTX_INITIALIZER;

static void
xamonxx_frame_pace_init(void)
{
   simple_mtx_lock(&xamonxx_pace_lock);
   if (!p_atomic_read(&xamonxx_pace_state)) {
      int fps = XAMONXX_FPS_CAP;
      const char *opt = os_get_option("XAMONXX_FPS_CAP");

      if (opt && opt[0])
         fps = atoi(opt);
      if (fps < 10 || fps > 240)
         fps = 0;

      if (fps) {
         xamonxx_pace_interval_ns = 1000000000ull / (uint64_t)fps;
         mesa_logi("xamonxx mali7300: frame pacer %d fps (%.3f ms)", fps,
                   xamonxx_pace_interval_ns / 1e6);
      } else {
         mesa_logi("xamonxx mali7300: frame pacer off");
      }
      p_atomic_set(&xamonxx_pace_state, fps ? 2 : 1);
   }
   simple_mtx_unlock(&xamonxx_pace_lock);
}

/* Called once per frame, before the image is handed to the presentation
 * engine. Blocks the presenting thread until the frame's deadline. */
static inline void
xamonxx_frame_pace(void)
{
   /* Acquire: pairs with p_atomic_set() in init, so interval is visible. */
   int state = p_atomic_read(&xamonxx_pace_state);

   if (unlikely(!state)) {
      xamonxx_frame_pace_init();
      state = p_atomic_read(&xamonxx_pace_state);
   }
   if (likely(state != 2))
      return;

   const uint64_t interval = xamonxx_pace_interval_ns;
   const uint64_t now = os_time_get_nano();
   uint64_t deadline;

   simple_mtx_lock(&xamonxx_pace_lock);
   deadline = xamonxx_pace_next_ns;
   if (!deadline || now > deadline + interval) {
      /* First frame, or more than one frame late: re-sync, no burst. */
      xamonxx_pace_next_ns = now + interval;
      simple_mtx_unlock(&xamonxx_pace_lock);
      return;
   }
   xamonxx_pace_next_ns = deadline + interval;
   simple_mtx_unlock(&xamonxx_pace_lock);

   if (deadline > now) {
      const struct timespec ts = {
         .tv_sec = (time_t)(deadline / 1000000000ull),
         .tv_nsec = (long)(deadline % 1000000000ull),
      };
      while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &ts, NULL) == EINTR)
         ;
   }
}
/* -------------------------------------------------------------------------- */

VKAPI_ATTR VkResult VKAPI_CALL
panvk_QueuePresentKHR('''

src = must_replace(src, "VKAPI_ATTR VkResult VKAPI_CALL\npanvk_QueuePresentKHR(", PACER,
                   "panvk_QueuePresentKHR definition")

src = must_replace(
    src,
    "panvk_QueuePresentKHR(VkQueue queue, const VkPresentInfoKHR *pPresentInfo)\n{\n",
    "panvk_QueuePresentKHR(VkQueue queue, const VkPresentInfoKHR *pPresentInfo)\n{\n"
    "   xamonxx_frame_pace();\n\n",
    "panvk_QueuePresentKHR body")

src = must_replace(
    src,
    "                                     VkImage image, int *pNativeFenceFd)\n{\n",
    "                                     VkImage image, int *pNativeFenceFd)\n{\n"
    "   xamonxx_frame_pace();\n\n",
    "panvk_QueueSignalReleaseImageANDROID body")

path.write_bytes(src.encode("utf-8"))  # LF on every host
print("xamonxx frame pacer: applied (default from XAMONXX_FPS_CAP macro)")
