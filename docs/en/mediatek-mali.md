# MediaTek / ARM Mali on DroidSpaces

## GPU selection

The batch workflow now has **GPU profile**:

- `qualcomm-kgsl`: existing Snapdragon Adreno integration and optional Qualcomm-oriented Mesa packages.
- `mediatek-mali`: **never installs the Qualcomm KGSL Mesa packages** and does not write `KGSL`, `FD_FORCE_KGSL`, or Qualcomm 8 Gen 2 workarounds into the rootfs. All distro/desktop combinations still use the normal package manager and normal upstream AnLand compositor integration.

**This is a safe Mali compatibility baseline, not a guarantee that AnLand rendering or 3D acceleration works on arbitrary MTK kernels.** In the MediaTek profile the separate `enable_mesa` checkbox is intentionally ignored (effective value `false`), because the bundled Mesa installer targets Adreno/KGSL and also includes an MSM-specific VA-API driver.

## What is required for hardware acceleration

DroidSpaces recognizes Mali GPU nodes such as `/dev/mali0`, but **device access by itself is insufficient**. AnLand expects a patched Wayland compositor and Android-compatible exported GPU buffers / DMA-BUF import, correctly shared between the container and Android app. The proprietary Android Mali **kbase** driver (`/dev/mali0`) is not automatically the open-source DRM Panfrost kernel driver (`/dev/dri/renderD128`). A distro Mesa Panfrost userspace driver works when the compatible kernel interface is actually present; a stock Android kbase interface may need a different userspace solution, tailored to the SoC/kernel.

Many of the current AnLand compositor desktop profiles use `ANLAND_DRM_DEVICE=/dev/dri/renderD128`. If your Android MTK kernel exposes only `/dev/mali0`, do not create a fake DRM device or change that environment variable to `/dev/mali0` without porting the compositor/producer. The two interfaces are not interchangeable.

## First host diagnostics (Android, adb connected)

```bash
adb shell su -c 'ls -l /dev/mali* /dev/dri/* /dev/dma_heap/* 2>/dev/null'
adb shell su -c 'getprop ro.board.platform; getprop ro.hardware'
adb shell su -c 'cat /proc/version'
adb shell su -c 'dmesg 2>/dev/null | grep -Ei "mali|panfrost|drm|dma.heap" | tail -n 60'
```

Do not assume `dmesg` is readable with SELinux enforcing. The node listings and kernel/SoC model are enough to decide the next step. Preserve permissions and SELinux enforcing initially; follow DroidSpaces/AnLand's official GPU Access and AnLand Display settings.

Inside the RootFS, check `ls -l /dev/mali* /dev/dri/*`, `eglinfo`, and (for X11) `glxinfo -B` if available. For a robust fallback on Mali devices, configure **Termux:X11 + VirGL** in DroidSpaces rather than AnLand. Do not enable both AnLand Display and Termux:X11 simultaneously in one container; use separate containers for experimentation.

## Suggested combinations

- Arch + KDE Mobile with `mediatek-mali` to probe native AnLand: experimental until GPU buffer import works.
- Arch + Niri with `mediatek-mali`: experimental; the patched compositor still needs host GPU buffer interop.
- Debian 13 + KDE/X11 using separate Termux:X11 + VirGL: better fallback when AnLand's DRM path is not supported.
- Arch + GNOME currently requires a compatible patched Mutter 51 release *independently* of any Mali work.

Remember that changing the GPU profile does not change the installed GPU driver in the Android kernel.
