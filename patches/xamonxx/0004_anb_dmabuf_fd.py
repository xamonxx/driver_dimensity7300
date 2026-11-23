#!/usr/bin/env python3
"""xamonxx 0004: find the real dma-buf in a swapchain (ANB) gralloc handle.

Root cause of the V0.1/V0.2 force close (owner log GameCrash-20261124-003913.txt,
GTA V launcher com.thegwchr.fuzzy on Infinix X6857 / MT6878):

    E MESA : GetMemoryFdPropertiesKHR failed
    F GTAV : vkCreateSwapchainKHR(...) failed (VkResult -1000072003)   // INVALID_EXTERNAL_HANDLE

The Android loader's swapchain hands each gralloc buffer to the driver as a
VkNativeBufferANDROID. vk_android_import_anb_memory() takes anb->handle->data[0]
as the dma-buf, but on MediaTek's Mali gralloc data[0] is not always the dma-buf
(the kbase GetMemoryFdPropertiesKHR path rejects any fd that lseek(SEEK_END) can't
size). The same tree already knows this for AHBs: panvk_android_find_dma_buf_fd()
and the AHB probe walk every fd ("Arm gralloc4 handles do not always put the
dma-buf at data[0]"). Only the ANB swapchain path still hard-codes data[0].

Fix: walk handle->data[0..numFds-1] and use the first fd that fstat()s, has a size,
is at least as large as the image needs, and that GetMemoryFdPropertiesKHR accepts.
data[0] stays the first candidate, so handles that already worked are unchanged.
"""
import sys
from pathlib import Path

path = Path("src/vulkan/runtime/vk_android.c")
src = path.read_text(encoding="utf-8")

if "xamonxx_anb_find_dma_buf" in src:
    print("xamonxx anb dma-buf: already applied")
    sys.exit(0)


def must_replace(text, old, new, what):
    n = text.count(old)
    if n != 1:
        sys.exit(f"xamonxx anb dma-buf: anchor '{what}' found {n}x (expected 1)")
    return text.replace(old, new, 1)


HELPER = r'''/* xamonxx 0004: Mali/MediaTek gralloc handles do not always carry the
 * dma-buf at data[0] (same rule as panvk_android_find_dma_buf_fd for AHBs).
 * Returns the first fd that is a sizeable dma-buf large enough for the image
 * and accepted by GetMemoryFdPropertiesKHR, or -1. */
static int
xamonxx_anb_find_dma_buf(struct vk_device *device, const native_handle_t *handle,
                         VkDeviceSize min_size,
                         VkMemoryFdPropertiesKHR *fd_props)
{
   /* Pass 0: big enough for the image. Pass 1: any sizeable dma-buf, as the
    * original data[0] path did (gralloc may size AFBC buffers differently). */
   for (int pass = 0; pass < 2; pass++) {
      for (int i = 0; i < handle->numFds; i++) {
         const int fd = handle->data[i];
         if (fd < 0)
            continue;

         struct stat st;
         if (fstat(fd, &st) < 0)
            continue;

         const off_t size = lseek(fd, 0, SEEK_END);
         lseek(fd, 0, SEEK_SET);
         if (size <= 0 || (pass == 0 && (VkDeviceSize)size < min_size))
            continue;

         if (device->dispatch_table.GetMemoryFdPropertiesKHR(
                (VkDevice)device, VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT,
                fd, fd_props) != VK_SUCCESS)
            continue;

         if (i != 0 || pass != 0)
            mesa_logi("vk_android: swapchain dma-buf = gralloc fd #%d of %d "
                      "(%lld bytes, image needs %llu, pass %d)", i,
                      handle->numFds, (long long)size,
                      (unsigned long long)min_size, pass);
         return fd;
      }
   }
   return -1;
}

VkResult
vk_android_import_anb_memory(struct vk_device *device,'''

src = must_replace(src, "VkResult\nvk_android_import_anb_memory(struct vk_device *device,", HELPER,
                   "vk_android_import_anb_memory definition")

OLD_BODY = """   int dma_buf_fd = anb->handle->data[0];

   /* Query image memory requirements for size and supported memory types */
   VkMemoryRequirements mem_reqs;
   device->dispatch_table.GetImageMemoryRequirements(
      (VkDevice)device, (VkImage)image, &mem_reqs);

   VkMemoryFdPropertiesKHR fd_props = {
      .sType = VK_STRUCTURE_TYPE_MEMORY_FD_PROPERTIES_KHR,
   };
   VkResult result = device->dispatch_table.GetMemoryFdPropertiesKHR(
      (VkDevice)device, VK_EXTERNAL_MEMORY_HANDLE_TYPE_DMA_BUF_BIT_EXT,
      dma_buf_fd, &fd_props);
   if (result != VK_SUCCESS) {
      mesa_loge("GetMemoryFdPropertiesKHR failed");
      return result;
   }
"""
NEW_BODY = """   VkResult result;

   /* Query image memory requirements for size and supported memory types */
   VkMemoryRequirements mem_reqs;
   device->dispatch_table.GetImageMemoryRequirements(
      (VkDevice)device, (VkImage)image, &mem_reqs);

   VkMemoryFdPropertiesKHR fd_props = {
      .sType = VK_STRUCTURE_TYPE_MEMORY_FD_PROPERTIES_KHR,
   };
   int dma_buf_fd = xamonxx_anb_find_dma_buf(device, anb->handle,
                                             mem_reqs.size, &fd_props);
   if (dma_buf_fd < 0) {
      mesa_loge("GetMemoryFdPropertiesKHR failed: no usable dma-buf among %d "
                "gralloc fds (image needs %llu bytes)", anb->handle->numFds,
                (unsigned long long)mem_reqs.size);
      return VK_ERROR_INVALID_EXTERNAL_HANDLE;
   }
"""
src = must_replace(src, OLD_BODY, NEW_BODY, "anb import body")

if "#include <sys/stat.h>" not in src:
    src = must_replace(src, "#include <unistd.h>\n", "#include <unistd.h>\n#include <sys/stat.h>\n",
                       "unistd include")

path.write_bytes(src.encode("utf-8"))
print("xamonxx anb dma-buf: applied")
