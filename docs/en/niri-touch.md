# Niri Touch on Arch ARM64 (DroidSpaces + AnLand)

A touch-oriented **Niri Touch** default is bundled directly with the Arch + Niri RootFS build. The files are installed to `/etc/skel` before the user is created, so new users get them in `~/.config` and `~/.local/bin` without downloading third-party dotfiles.

## What is included

- Niri: 92%-width main column, rounded corners, comfortable gaps and visible focus, overview hot corner and drag-to-edge scrolling
- Waybar: large bottom touch dock (launcher, terminal, files, overview, workspace buttons, volume, battery, time, keyboard)
- Fuzzel: large-text application launcher; Foot: legible terminal; Thunar: lightweight file manager; Mako: compact notifications; Swaybg: dark solid wallpaper
- Squeekboard: on-screen keyboard, with a keyboard toggle in the dock via its D-Bus interface
- No login to external dotfiles repositories, tracking, or remote install scripts

**The configuration is a starter theme, not a replacement for working AnLand display drivers.** It is delivered for both Qualcomm and MTK GPU profiles. On MTK the profile no longer injects KGSL variables or blindly forces /dev/dri/renderD128; actual graphics support depends on the Android host/kernel and the patched compositor.

Files:
- `~/.config/niri/config.kdl`
- `~/.config/waybar/config.jsonc`, `style.css`
- `~/.config/fuzzel/fuzzel.ini`
- `~/.config/foot/foot.ini`
- `~/.config/mako/config`
- `~/.local/bin/droidspaces-osk-toggle`

To verify the theme on a running system:
```bash
niri-anland validate --config "$HOME/.config/niri/config.kdl"
```
If your `niri-anland` build does not support `validate`, check `niri-anland --help` and test with the actual binary. Testing standard upstream Niri alone does **not** prove an AnLand-patched compositor is operational. Squeekboard requires the compositor's Wayland input-method protocol; some AnLand forks may require adapting its text-input integration.

Use the bottom bar's overview and workspace controls when using a touchscreen without a physical keyboard. The upstream Niri touchscreen overview supports one-finger scrolling and long-press window dragging; its 3-finger workspace gestures are primarily touchpad features, not assumed on Android touchscreens.
