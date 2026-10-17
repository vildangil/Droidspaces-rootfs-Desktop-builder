[Documentation index](README.md) · [Project home](../../README_english.md)

# Build Options

Choose the target, desktop, display backend, and optional features on the GitHub Actions `Run workflow` page. Desktop images are intended for ARM64 Droidspaces containers.

## Distribution and desktop support

| Target | Base image | Desktop profiles | Anland Wayland |
| --- | --- | --- | --- |
| `Debian-13` | Debian 13 (trixie) | `none`, `KDE`, `KDE mobile`, `GNOME`, `Anland Next` | Yes |
| `Ubuntu-24` | Ubuntu 24.04 | `none`, `KDE` | No |
| `Ubuntu-25` | Ubuntu 25.10 | `none`, `KDE` | No |
| `Ubuntu-26` | Ubuntu 26.04 | `none`, `KDE`, `KDE mobile`, `GNOME`, `Anland Next` | Yes |
| `Fedora-43` | Fedora 43 | `none`, `KDE`, `KDE mobile`, `Anland Next` | Yes |
| `Fedora-44` | Fedora 44 | `none`, `KDE`, `KDE mobile`, `Anland Next` | Yes |
| `Arch` | Arch Linux ARM | `none`, `KDE`, `KDE mobile`, `GNOME`, `Anland Next`, `Niri` | Yes |

`all` filters targets according to desktop/backend support. `all-wayland` builds five Wayland targets for KDE/KDE Mobile; GNOME builds Debian 13, Ubuntu 26, and Arch Linux; Niri builds Arch only. GNOME, KDE Mobile, Anland Next, and Niri force `anland-wayland`.

| Desktop | Description |
| --- | --- |
| `none` | Command-line environment for SSH, development, or a custom desktop. |
| `KDE` | KDE Plasma; X11 or Anland Wayland, depending on the target. |
| `KDE mobile` | Touch-first Plasma Mobile; requires Anland Wayland. |
| `GNOME` | Anland Wayland only, on Debian 13, Ubuntu 26, and Arch Linux ARM. |
| `Anland Next` | An Anland session with rootless Xwayland and mini-wm, without a full desktop; Wayland only. |
| `Niri` | An Anland Niri scrollable-tiling Wayland compositor on Arch Linux ARM; Wayland only. |

## Workflow inputs

| Input | Values / default | Description |
| --- | --- | --- |
| `build_target` | Distribution, `all`, `all-wayland`; default `Debian-13` | Select build targets. |
| `custom_username` | 1–32 letters, digits, `_`, or `-`, starting with a letter or `_`; default `arch` | Normal RootFS user. |
| `desktop` | `none`, `KDE`, `KDE mobile`, `GNOME`, `Anland Next`, `Niri`; default `KDE` | Select desktop or command-line mode. |
| `desktop_autostart` | `true` / `false`; default `true` | Installs the desktop startup service; must be disabled for `none`. |
| `display_backend` | `x11` / `anland-wayland` | Defaults to Wayland in the Chinese workflow and X11 in the English workflow; some profiles force Wayland. |
| `PulseAudio` | `socket` / `tcp` / `none`; default `socket` | X11 audio forwarding; Anland sets this to `none`. |
| `enable_zh_tz` | `true` / `false` | Installs Chinese locale and Shanghai timezone; defaults differ by workflow. |
| `gpu_profile` | `qualcomm-kgsl` / `mediatek-mali`; default `qualcomm-kgsl` | Single-build GPU profile; selected for English and Chinese workflows. |\n| `enable_mesa` | `true` / `false`; default `true` | Adds Qualcomm Snapdragon GPU/Mesa support *only* for the Qualcomm profile; automatically disabled for Mali. |
| `enable_8gen2_wayland` | `true` / `false`; default `false` | Sets the Snapdragon 8 Gen 2 Turnip UBWC workaround only on the Qualcomm profile; disabled on Mali. |
| `nosnap` | `true` / `false` | Ubuntu only: removes Snap and prevents APT from reinstalling it; defaults differ by workflow. |
| `enable_systemd257` | `true` / `false`; default `false` | Tries the systemd 257 package family for old Android kernels; only `none` and standard `KDE` are supported. |
| `enable_srf` | `true` / `false` | Installs Fcitx5; enabled by default in the Chinese workflow, disabled in English. |
| `enable_binfmt` | `true` / `false`; default `false` | Adds binfmt cross-architecture support; not recommended for Arch. |
| `enable_yj` | `true` / `false`; default `true` | Improves NAT and Android/Droidspaces hardware recognition. |
| `enable_kfgj` | `true` / `false`; default `false` | Installs development tools such as compilers, CMake, and Python. |
| `enable_zip` | `true` / `false`; default `true` | Installs common compression tools. |
| `enable_docker` | `true` / `false`; default `false` | Installs Docker packages in the RootFS. |
| `wayland_package_repository` | Public `owner/repository`; default `Goldzxcbug/droidspaces-package` | Selects the source for prebuilt Anland package Releases, including Arch GNOME Mutter. |

For exact defaults, see `.github/workflows/build-rootfs-releases-en.yml` and `build-rootfs-releases.yml`. The multi-select workflow offers **two independent GPU checkboxes** (Qualcomm and MediaTek); both are selected by default. It builds each compatible desktop for both GPUs and publishes them as separately named archives in one release. See [Batch builds](batch-builds.md). `enable_systemd257` is experimental and adds build time. Systems already at systemd 257 or older skip installation; details are in the [script guide](../../scripts/README_english.md).

## Browser and lightweight desktop defaults

Graphical RootFS builds use **Firefox**, not Google Chrome. CLI-only (`none`) images do not install a browser. Native distribution packages are used where possible:

| Distribution | Browser source |
| --- | --- |
| Debian 13 | `firefox-esr` from Debian |
| Ubuntu 24/25/26 | `firefox` DEB from Mozilla's signed APT repository, **not** Ubuntu's Snap transitional package |
| Fedora 43/44 | `firefox` from Fedora |
| Arch Linux ARM | `firefox` from Arch Linux ARM (`extra`, aarch64) |

The existing Google Chrome AUR build and external Google package repositories have been removed from the RootFS build. Firefox becomes the default handler for web links and HTML. The Mozilla APT key fingerprint is checked during Ubuntu builds.

To avoid unnecessary duplicate tools, the Niri profile uses **Foot** and **Thunar** instead of installing Alacritty alongside Foot and Nautilus as its file manager. KDE Mobile no longer installs Angelfish by default; Firefox remains available. Optional GPU benchmark applications `glmark2` and `vkmark` are excluded from the default desktop package lists (they can be installed later with the distro package manager).

Firefox is not guaranteed to use less RAM than Chrome for every workload. This change primarily reduces package duplication and avoids installing Chrome through AUR/Snap dependencies.

## Generated Droidspaces recommendations

Native and QEMU builds generate `container.config` from the effective build options.
It is the first regular archive member, followed by the rootfs and then XZ compression.
Old root-level copies are removed; no additional Dockerfile `COPY` is needed.
Droidspaces versions with recommendation support prefill their installation wizard.

| Build option | Recommended setting |
| --- | --- |
| `anland-wayland` | `enable_anland=1`; Termux:X11 and PulseAudio off |
| `x11` | `enable_termux_x11=1`; Anland off |
| X11 with `socket` audio | `enable_pulseaudio=1`; other audio choices use `0` |
| KDE or KDE Mobile | `allow_userns=1` |
| Docker enabled | `net_mode=nat`; otherwise keep the app default |
| Snapdragon GPU support enabled | `enable_gpu_mode=1` |
| Anland Next | `bind_mounts=/data/local/tmp/awl:/run/anland` |
| `enable_zh_tz=true` (Chinese locale and Shanghai timezone) | `dns_servers=114.114.114.114` |

Keys follow the Droidspaces Anland branch. Mount paths live in the config and use
the existing Droidspaces bind-mount parser and runtime. Environment variables are
not passed through this recommendation file. On kernels without user namespaces,
the requested KDE setting stays checked but disabled; this does not add kernel support.

Run the mapping and archive checks with `python3 -m unittest discover -s tests -v`.
