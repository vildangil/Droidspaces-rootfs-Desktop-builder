#!/usr/bin/env bash
# Validate that the legacy systemd-257 runtime can be combined with the
# desktop actually requested. Never silently downgrade a desktop to CLI.
validate_legacy_desktop() {
    local enabled="${1:?}" desktop="${2:?}" target="${3:?}"
    case "$enabled" in
        false) return 0 ;;
        true)
            case "$desktop" in
                none|kde) return 0 ;;
                niri)
                    if [[ "$target" == "Arch" ]]; then
                        return 0
                    fi
                    echo "systemd 257 + Niri is experimental and only supported for Arch (got: $target)" >&2
                    return 1
                    ;;
                *)
                    echo "systemd 257 cannot be combined with $desktop (supported: none, KDE, Arch Niri)" >&2
                    return 1
                    ;;
            esac
            ;;
        *)
            echo "Invalid legacy systemd 257 flag: $enabled (use true or false)" >&2
            return 1
            ;;
    esac
}
