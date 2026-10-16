# Batch RootFS builds (checkbox multi-select)

Use **Actions → Build multiple Droidspaces RootFS (multi-select) → Run workflow**.

Select any number of distributions and desktop environments using GitHub's boolean checkboxes. The workflow builds each supported distribution/desktop pair on a native ARM64 runner and publishes a **separate Release** for each pair. It leaves the original single-target workflows unchanged.

The default example enables:
- Arch + GNOME
- Arch + Niri

Debian 13 and every other distribution are off by default. Check their boxes explicitly to include them.

## Supported combinations

Compatibility comes directly from `scripts/lib/desktop-config.sh`, so the batch planner stays in sync with the original builder.

- GNOME: Arch, Debian 13, Ubuntu 26.
- Niri: Arch only.
- KDE Mobile and Anland Next: Arch, Debian 13, Ubuntu 26, Fedora 43 and 44.
- KDE Plasma + AnLand: Arch, Debian 13, Ubuntu 26, Fedora 43 and 44.
- KDE Plasma + X11 and CLI-only: all seven distributions (including Ubuntu 24/25).

Unsupported combinations are **skipped**, not converted silently into another desktop/backend. The Plan job summary lists what will be built; the job fails if nothing compatible was selected.

For desktop `none`, the workflow always uses the CLI backend and disables desktop auto-start. For GNOME, Niri, Anland Next, and KDE Mobile, it uses AnLand Wayland. For ordinary KDE, use the `kde_backend` choice.

## Releases and performance

Each pair gets a unique artifact namespace and Release tag based on the GitHub run ID, attempt, distro, and desktop. This prevents parallel runs from collecting the wrong archives or publishing to the same tag.

Up to three target/profile builds run in parallel. A base RootFS from one Linux distribution is **not** reused for another distribution, and graphical sessions need their own desktop-specific packages. This intentionally preserves the upstream builder's package and AnLand integration.

All other advanced build options remain available through the upstream single-target workflow. View the planner and individual build jobs in the Actions page. Find each resulting `.tar.xz` archive on the repository's Releases page.

**First boot:** change the default password after importing the rootfs. See [Quick Start](quick-start.md) and [AnLand setup](desktop-and-anland.md).

## Arch GNOME ABI compatibility

Arch Linux ARM is rolling-release. If its `gnome-shell` package depends on `libmutter-51.so` while the upstream AnLand GNOME release supplies patched Mutter 50 (`libmutter-50.so`), the rootfs build cannot produce a functioning GNOME AnLand desktop. The installer now reports this mismatch explicitly instead of suggesting that a forced pacman downgrade will help. Rebuild/update the corresponding patched Mutter in the separate `droidspaces-package` repository and set `wayland_package_repository` to that fork when its release is ready. Niri does not depend on GNOME's Mutter ABI.
