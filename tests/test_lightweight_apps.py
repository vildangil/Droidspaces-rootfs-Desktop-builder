"""Verify the browser and smaller default app selection in ARM64 RootFS builds."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILES = [
    "Arch.Dockerfile", "Debian-13.Dockerfile",
    "Ubuntu-24.Dockerfile", "Ubuntu-25.Dockerfile",
    "Ubuntu-26.Dockerfile", "Fedora-43.Dockerfile",
    "Fedora-44.Dockerfile",
]

class LightweightAppsTests(unittest.TestCase):
    def test_all_dockerfiles_install_firefox_not_chrome(self):
        for path in DOCKERFILES:
            data = (ROOT / path).read_text()
            with self.subTest(path=path):
                self.assertIn("COPY scripts/configure-firefox.sh", data)
                self.assertIn("RUN /usr/local/sbin/configure-firefox", data)
                self.assertNotIn("configure-chrome", data)
                self.assertNotIn("google-chrome", data)

    def test_native_firefox_packages(self):
        data = (ROOT / "scripts/configure-firefox.sh").read_text()
        for text in (
            "firefox-esr", "pacman -S --noconfirm --needed firefox",
            "dnf install -y --setopt=install_weak_deps=False firefox",
            "packages.mozilla.org/apt", "Architectures: arm64",
            "35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3",
            "Pin: release o=Ubuntu", "Pin-Priority: -1",
            "none) exit 0",
        ):
            self.assertIn(text, data)
        self.assertNotIn("snap install", data)
        self.assertNotIn("dl.google.com", data)
        self.assertNotIn("aur.archlinux.org", data)

    def test_duplicated_apps_removed(self):
        niri = (ROOT / "scripts/desktops/niri.sh").read_text()
        mobile = (ROOT / "scripts/desktops/kde-mobile.sh").read_text()
        self.assertIn("foot thunar fuzzel", niri)
        self.assertNotRegex(niri, r"\balacritty\b|\bnautilus\b")
        self.assertNotRegex(mobile, r"\bangelfish\b")
        panel = (ROOT / "dotfiles/niri/.config/waybar/config.jsonc").read_text()
        self.assertIn('"on-click": "thunar"', panel)

    def test_no_gpu_benchmarks_preinstalled(self):
        for path in (ROOT / "scripts/desktops").glob("*.sh"):
            self.assertNotRegex(path.read_text(), r"\b(glmark2|vkmark)\b")

if __name__ == "__main__":
    unittest.main()
