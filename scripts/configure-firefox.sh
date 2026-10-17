#!/usr/bin/env bash
# Install a native ARM64 Firefox browser instead of Google Chrome / Chromium.
# Keep all package installation with the distro package manager, never Snap or AUR.
set -euo pipefail

desktop="${1:-}"
display_backend="${2:-}"
rootfs="${ROOTFS_DIR:-}"

case "$desktop" in
    none) exit 0 ;;
    kde|kde-mobile|gnome|niri|anland-next) ;;
    *) echo "Unknown desktop: $desktop" >&2; exit 1 ;;
esac
case "$display_backend" in
    x11|anland-wayland) ;;
    *) echo "Unknown display backend: $display_backend" >&2; exit 1 ;;
esac

# ROOTFS_DIR is used for isolated tests; normal image builds run directly in /.
[[ -z "$rootfs" ]] || exit 0

source /etc/os-release
browser_cmd=firefox
desktop_file=firefox.desktop

install_mozilla_ubuntu_deb() {
    # Ubuntu's 'firefox' apt package is a Snap transition package. A normal
    # DroidSpaces container should not require snapd just to open a web page.
    apt-get install -y --no-install-recommends ca-certificates curl gnupg
    install -d -m 0755 /etc/apt/keyrings /etc/apt/sources.list.d /etc/apt/preferences.d
    curl --proto '=https' --tlsv1.2 -fsSL \
        https://packages.mozilla.org/apt/repo-signing-key.gpg \
        -o /etc/apt/keyrings/packages.mozilla.org.asc
    local expected=35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3 actual
    actual="$(gpg --batch --show-keys --with-colons /etc/apt/keyrings/packages.mozilla.org.asc |
        awk -F: '$1 == "fpr" { print $10; exit }')"
    if [[ "$actual" != "$expected" ]]; then
        echo "Mozilla APT signing-key fingerprint mismatch" >&2
        exit 1
    fi

    cat > /etc/apt/sources.list.d/mozilla.sources <<'EOF'
Types: deb
URIs: https://packages.mozilla.org/apt
Suites: mozilla
Components: main
Architectures: arm64
Signed-By: /etc/apt/keyrings/packages.mozilla.org.asc
EOF
    # Pin the real DEB package above the Snap transitional package.
    cat > /etc/apt/preferences.d/droidspaces-firefox <<'EOF'
Package: firefox
Pin: origin packages.mozilla.org
Pin-Priority: 1001

Package: firefox
Pin: release o=Ubuntu
Pin-Priority: -1
EOF

    apt-get update
    apt-get install -y --no-install-recommends firefox
    if dpkg-query -W -f='${Version}' firefox | grep -qi 'snap'; then
        echo "Firefox resolved to an Ubuntu Snap transition; refusing it." >&2
        exit 1
    fi
}

case "${ID:-}" in
    debian)
        apt-get install -y --no-install-recommends firefox-esr
        browser_cmd=firefox-esr
        desktop_file=firefox-esr.desktop
        ;;
    ubuntu) install_mozilla_ubuntu_deb ;;
    fedora) dnf install -y --setopt=install_weak_deps=False firefox ;;
    arch|archarm|archlinux) pacman -S --noconfirm --needed firefox ;;
    *) echo "Unsupported Firefox distribution: ${ID:-unknown}" >&2; exit 1 ;;
esac

command -v "$browser_cmd" >/dev/null || {
    echo "Firefox package did not install the expected executable: $browser_cmd" >&2
    exit 1
}
if [[ ! -f "/usr/share/applications/$desktop_file" ]]; then
    echo "Firefox desktop entry missing: $desktop_file" >&2
    exit 1
fi

# Make Firefox the browser for HTML and web links in X11/Wayland desktops.
install -d -m 0755 /etc/xdg
cat > /etc/xdg/mimeapps.list <<EOF
[Default Applications]
text/html=$desktop_file
application/xhtml+xml=$desktop_file
x-scheme-handler/http=$desktop_file
x-scheme-handler/https=$desktop_file
EOF

# Firefox 2026 supports native Wayland. Don't force a Qualcomm GPU/DRM node:
# on Android/MTK this might not exist and would break the browser.
printf '[droidspaces] Installed native Firefox (%s) for %s/%s\n' \
    "$browser_cmd" "$desktop" "$display_backend"
