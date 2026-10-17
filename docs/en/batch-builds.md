# Batch RootFS builds (checkbox multi-select)

Use **Actions → Build multiple Droidspaces RootFS (multi-select) → Run workflow**.

Select any number of distributions and desktop environments using GitHub's boolean checkboxes. The workflow builds each supported distribution/desktop pair on native ARM64 runners and publishes **one GitHub Release containing every successful archive** after the entire batch succeeds. It leaves the original single-target workflows unchanged.

The default example enables:
- Arch + Niri
- Both Qualcomm (Adreno/KGSL) **and** MediaTek (Mali) GPU profiles, resulting in **two distinct archives**

Arch + GNOME is available as an explicit opt-in, but currently requires rebuilt Mutter packages matching the rolling Arch `gnome-shell` ABI.

Debian 13 and every other distribution are off by default. Check their boxes explicitly to include them.

## GPU family

Use independent `gpu_qualcomm` and `gpu_mediatek` checkboxes. When both are checked, **every supported distribution/desktop combination is built twice**, once per GPU profile. By default both are enabled; you can disable either one. Selecting neither fails before any build is scheduled.

For a single build, choose `gpu_profile=qualcomm-kgsl` or `gpu_profile=mediatek-mali` in either the English or Chinese workflow. The MediaTek/Mali profile turns off the Qualcomm-only KGSL Mesa installer and Snapdragon 8 Gen 2 workarounds, regardless of their checkbox values. It does **not** automatically enable native Mali hardware acceleration for AnLand. See [MediaTek / ARM Mali support](mediatek-mali.md) for required kernel GPU buffer interfaces and an X11/VirGL fallback.

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

Each distribution/desktop/GPU combination gets a unique intermediate Actions artifact namespace based on the GitHub run ID, attempt, distro, desktop and GPU. **One batch Release tag** is generated from the run ID and attempt; no individual pair creates a Release. This prevents parallel runs from collecting the wrong archives.

Up to three target/profile builds run in parallel. A base RootFS from one Linux distribution is **not** reused for another distribution or GPU choice, and graphical sessions need their own desktop-specific packages. This intentionally preserves the upstream builder's package and AnLand integration.

All other advanced build options remain available through the upstream single-target workflow. View the planner and individual build jobs in the Actions page. Find all `.tar.xz` archives together under a **single** repository Release when the entire batch succeeds.

**First boot:** change the default password after importing the rootfs. See [Quick Start](quick-start.md) and [AnLand setup](desktop-and-anland.md).

## Arch GNOME ABI compatibility

Arch Linux ARM is rolling-release. If its `gnome-shell` package depends on `libmutter-51.so` while the upstream AnLand GNOME release supplies patched Mutter 50 (`libmutter-50.so`), the rootfs build cannot produce a functioning GNOME AnLand desktop. The installer now reports this mismatch explicitly instead of suggesting that a forced pacman downgrade will help. Rebuild/update the corresponding patched Mutter in the separate `droidspaces-package` repository and set `wayland_package_repository` to that fork when its release is ready. Niri does not depend on GNOME's Mutter ABI.

## Single GitHub Release

The batch workflow invokes the reusable core with `publish_release: false`, disabling per-combination Releases. Once **all** selected matrix builds (including both GPU variants, if checked) succeed, one final job downloads the archives for the current run and attempt only, verifies that the archive count matches the planned matrix, stages **one** draft release with tag `batch-<run_id>-<attempt>`, and publishes it. A failed build leaves its artifact accessible under the Actions run for debugging but produces no partial GitHub Release. Standalone build workflows keep the prior behavior.
