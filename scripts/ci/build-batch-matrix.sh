#!/usr/bin/env bash
# Build a compatibility-checked Cartesian product for GitHub Actions.
# Reuse the main builder's compatibility definitions; do not duplicate the table.
set -euo pipefail

source scripts/lib/desktop-config.sh

targets=(Arch Debian-13 Ubuntu-24 Ubuntu-25 Ubuntu-26 Fedora-43 Fedora-44)
target_flags=(DISTRO_ARCH DISTRO_DEBIAN_13 DISTRO_UBUNTU_24 DISTRO_UBUNTU_25 DISTRO_UBUNTU_26 DISTRO_FEDORA_43 DISTRO_FEDORA_44)
desktops=(none kde kde-mobile gnome anland-next niri)
desktop_flags=(DESKTOP_NONE DESKTOP_KDE DESKTOP_KDE_MOBILE DESKTOP_GNOME DESKTOP_ANLAND_NEXT DESKTOP_NIRI)

selected_targets=()
selected_desktops=()
selected_gpus=()
if [[ "${GPU_QUALCOMM:-false}" == "true" ]]; then
  selected_gpus+=(qualcomm-kgsl)
fi
if [[ "${GPU_MEDIATEK:-false}" == "true" ]]; then
  selected_gpus+=(mediatek-mali)
fi
if (( ${#selected_gpus[@]} == 0 )); then
  echo "Select at least one GPU profile (Qualcomm or MediaTek)." >&2
  exit 1
fi
for i in "${!targets[@]}"; do
  flag="${target_flags[$i]}"
  if [[ "${!flag:-false}" == "true" ]]; then
    selected_targets+=("${targets[$i]}")
  fi
done
for i in "${!desktops[@]}"; do
  flag="${desktop_flags[$i]}"
  if [[ "${!flag:-false}" == "true" ]]; then
    selected_desktops+=("${desktops[$i]}")
  fi
done

if (( ${#selected_targets[@]} == 0 )); then
  echo "Select at least one distribution." >&2
  exit 1
fi
if (( ${#selected_desktops[@]} == 0 )); then
  echo "Select at least one desktop." >&2
  exit 1
fi

case "${LEGACY_SYSTEMD257:-false}" in
  true)
    # The older systemd package family is currently known to work with
    # CLI/KDE, and Niri on Arch is explicitly experimental. Never silently
    # replace a requested desktop with CLI in a multi-build run.
    for desktop in "${selected_desktops[@]}"; do
      case "$desktop" in
        none|kde|niri) ;;
        *)
          echo "systemd 257 is not supported for $desktop in the batch workflow; select none, KDE or Arch Niri." >&2
          exit 1
          ;;
      esac
    done
    ;;
  false) ;;
  *) echo "LEGACY_SYSTEMD257 must be true or false." >&2; exit 1 ;;
esac

case "${KDE_BACKEND:-anland-wayland}" in
  x11|anland-wayland) ;;
  *) echo "Unsupported KDE backend: $KDE_BACKEND" >&2; exit 1 ;;
esac

summary="${GITHUB_STEP_SUMMARY:-/dev/null}"
{
  echo "## Selected RootFS builds"
  echo
  echo "| Distribution | Desktop | GPU profile | Backend |"
  echo "| --- | --- | --- | --- |"
} >> "$summary"

matrix_items=()
skipped=0
for target in "${selected_targets[@]}"; do
  for desktop in "${selected_desktops[@]}"; do
    if [[ "$desktop" == none ]]; then
      backend=x11
    elif [[ "$desktop" == kde ]]; then
      backend="${KDE_BACKEND:-anland-wayland}"
    else
      backend=anland-wayland
    fi

    if desktop_backend_supported "$target" "$desktop" "$backend"; then
      for gpu in "${selected_gpus[@]}"; do
        matrix_items+=("$(jq -cn --arg target "$target" --arg desktop "$desktop" --arg backend "$backend" --arg gpu "$gpu" '{target:$target,desktop:$desktop,backend:$backend,gpu:$gpu}')")
        printf '| %s | %s | %s | %s |\n' "$target" "$desktop" "$gpu" "$backend" >> "$summary"
      done
    else
      echo "Skipping unsupported combination: $target / $desktop / $backend"
      ((skipped+=1))
    fi
  done
done

if (( ${#matrix_items[@]} == 0 )); then
  echo "No compatible build combinations. Use an AnLand-supported distro or KDE/X11." >&2
  exit 1
fi

matrix="$(printf '%s\n' "${matrix_items[@]}" | jq -cs '{include:.}')"
printf 'matrix=%s\n' "$matrix" >> "${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}"
echo "Scheduled ${#matrix_items[@]} builds; skipped $skipped unsupported combinations."
{
  echo
  echo "Scheduled **${#matrix_items[@]}** builds; skipped **$skipped** unsupported combinations."
  echo
  echo "All successfully built combinations are uploaded to one Release per workflow run."
} >> "$summary"
