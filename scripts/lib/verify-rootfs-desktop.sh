#!/usr/bin/env bash
# Check the *actual* export tar, not just requested Actions inputs. In
# particular Niri/systemd257 must never be published as an Arch-none image.
verify_rootfs_desktop_tar() {
    local archive="${1:?}" expected_desktop="${2:?}" expected_backend="${3:?}"
    local metadata members
    if ! metadata=$(tar -xOf "$archive" etc/droidspaces-desktop.conf 2>/dev/null); then
        if ! metadata=$(tar -xOf "$archive" ./etc/droidspaces-desktop.conf 2>/dev/null); then
            echo "RootFS export is missing etc/droidspaces-desktop.conf" >&2
            return 1
        fi
    fi
    if ! grep -Fxq -- "DESKTOP=$expected_desktop" <<< "$metadata"; then
        echo "Wrong RootFS desktop: expected '$expected_desktop', embedded config: $metadata" >&2
        return 1
    fi
    if ! grep -Fxq -- "DISPLAY_BACKEND=$expected_backend" <<< "$metadata"; then
        echo "Wrong RootFS backend: expected '$expected_backend', embedded config: $metadata" >&2
        return 1
    fi
    [[ "$expected_desktop" != "none" ]] || return 0
    if ! members=$(tar -tf "$archive"); then
        echo "Failed to list exported RootFS archive" >&2
        return 1
    fi
    if ! grep -Eq '^((\\./)?etc/systemd/system/desktop-session\\.service)$' <<< "$members"; then
        echo "Graphical RootFS export lacks desktop-session.service" >&2
        return 1
    fi
    if [[ "$expected_desktop" == "niri" ]]; then
        if ! grep -Eq '^((\\./)?usr/bin/niri-anland)$' <<< "$members"; then
            echo "Niri export has no /usr/bin/niri-anland; refusing to release a CLI-only image as Niri" >&2
            return 1
        fi
    fi
    printf 'Verified RootFS export desktop=%s backend=%s\n' "$expected_desktop" "$expected_backend"
}
