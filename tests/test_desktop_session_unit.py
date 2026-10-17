"""Verify non-destructive desktop session startup configuration."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/configure-desktop.sh"
UNIT = ROOT / "scripts/start/desktop-session.service"


class SessionUnitTests(unittest.TestCase):
    def configure(self, desktop, autostart, backend):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        parent = Path(temporary.name)
        guest = parent / "guest"
        (guest / "etc").mkdir(parents=True)
        (guest / "home" / "arch").mkdir(parents=True)
        profiles = parent / "profiles"
        profiles.mkdir()
        for name in ("niri", "kde", "kde-mobile", "gnome", "anland-next"):
            path = profiles / (name + ".sh")
            path.write_text("#!/bin/sh\nexit 0\n")
            path.chmod(0o755)
        env = dict(os.environ)
        env.update(
            ROOTFS_DIR=str(guest),
            START_TEMPLATES_DIR=str(UNIT.parent),
            DROIDSPACES_DESKTOP_PROFILE_DIR=str(profiles),
        )
        result = subprocess.run(
            ["bash", str(SCRIPT), desktop, backend, str(autostart).lower(), "arch"],
            cwd=ROOT, env=env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return guest

    def test_niri_unit_installed_and_enabled_for_autostart(self):
        guest = self.configure("niri", True, "anland-wayland")
        unit = guest / "etc/systemd/system/desktop-session.service"
        wanted = guest / "etc/systemd/system/multi-user.target.wants/desktop-session.service"
        self.assertEqual(unit.read_bytes(), UNIT.read_bytes())
        self.assertTrue(wanted.is_symlink())
        self.assertEqual(os.readlink(wanted), "/etc/systemd/system/desktop-session.service")
        self.assertIn("DESKTOP=niri", (guest / "etc/droidspaces-desktop.conf").read_text())

    def test_niri_unit_is_present_but_not_enabled_when_autostart_off(self):
        guest = self.configure("niri", False, "anland-wayland")
        unit = guest / "etc/systemd/system/desktop-session.service"
        wanted = guest / "etc/systemd/system/multi-user.target.wants/desktop-session.service"
        self.assertEqual(unit.read_bytes(), UNIT.read_bytes())
        self.assertFalse(wanted.exists())

    def test_kde_keeps_same_autostart_semantics(self):
        for autostart in (True, False):
            with self.subTest(autostart=autostart):
                guest = self.configure("kde", autostart, "x11")
                unit = guest / "etc/systemd/system/desktop-session.service"
                self.assertTrue(unit.is_file())
                self.assertEqual(
                    (guest / "etc/systemd/system/multi-user.target.wants/desktop-session.service").is_symlink(),
                    autostart,
                )

    def test_cli_does_not_install_desktop_service(self):
        guest = self.configure("none", False, "x11")
        self.assertFalse((guest / "etc/systemd/system/desktop-session.service").exists())


if __name__ == "__main__":
    unittest.main()
