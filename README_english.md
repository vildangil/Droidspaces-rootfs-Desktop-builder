English | [中文](README.md)

# Droidspaces RootFS Builder

Build ARM64 Linux RootFS images for Droidspaces on Android with GitHub Actions. Choose Debian, Ubuntu, Fedora, or Arch Linux, select KDE, KDE Mobile, GNOME, Anland Next, Arch Niri, or command-line mode, then import the generated `.tar.xz` archive into Droidspaces.

![Debian 13 KDE running with Anland Wayland](docs/images/debian-kde-wayland.jpg)

**Quick start:** Fork this repository → open `Actions` → run “Build and Release Droidspaces RootFS” → download the RootFS from `Releases`.

## What it provides

- Seven distribution targets, with X11 and Anland Wayland support depending on the selected profile and distribution.
- Qualcomm/Adreno and MediaTek/Mali GPU profiles (both selectable together in batch builds), optional Chinese locale, Fcitx5, audio forwarding, development tools, and Docker.
- Native Firefox by default in graphical images (Debian ESR, Mozilla DEB on Ubuntu, distro packages on Fedora/Arch); lighter Niri application selection.
- Automatic GitHub Release publishing, desktop session startup, USB management, and in-container maintenance tools.

## Documentation

- [Documentation index and desktop screenshots](docs/en/README.md)
- [Build with Actions and import into Droidspaces](docs/en/quick-start.md)
- [Batch-build multiple distributions and desktops using checkboxes](docs/en/batch-builds.md)
- [Supported distributions and build options](docs/en/build-options.md)
- [Desktop startup and Anland Wayland setup](docs/en/desktop-and-anland.md)
- [Niri Touch tablet-style desktop defaults](docs/en/niri-touch.md)
- [TUI, USB, firmware, and local builds](docs/en/advanced-usage.md)
- [Script maintenance guide](scripts/README_english.md)

## Targets

`Debian-13`, `Ubuntu-24`, `Ubuntu-25`, `Ubuntu-26`, `Fedora-43`, `Fedora-44`, and `Arch`. Niri is currently available only on Arch Linux ARM. See the [build options guide](docs/en/build-options.md) for desktop and display-backend compatibility.

## Acknowledgements

- [Droidspaces-OSS](https://github.com/ravindu644/Droidspaces-OSS/): runtime foundation.
- [mesa-for-android-container](https://github.com/lfdevs/mesa-for-android-container): Snapdragon GPU driver support.
- [droidspaces-media-decode](https://github.com/Re-s/droidspaces-media-decode): Android MediaCodec hardware decoding for containers.
- [Anland](https://github.com/superturtlee/anland): Wayland display backend and related work.
- [Droidspaces USB Manager](https://github.com/Yizhou147/Droidspaces-USB-Manager): USB storage and ADB device management.
- [ObsidianArc](https://github.com/OnyxAxisOwO/ObsidianArc): self-hosted multi-model chat gateway; thanks for providing public-benefit AI services.

---

[All desktop screenshots](docs/en/README.md#screenshots) · [中文 README](README.md)
