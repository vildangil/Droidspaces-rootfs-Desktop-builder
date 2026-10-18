"""Prevent accidentally publishing CLI images labelled Arch Niri on systemd 257."""
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "scripts/lib/legacy-desktop.sh"
VERIFY = ROOT / "scripts/lib/verify-rootfs-desktop.sh"


class LegacyNiriTests(unittest.TestCase):
    def check_legacy(self, flag, desktop, distro):
        return subprocess.run(
            ["bash", "-c", 'source "$1"; validate_legacy_desktop "$2" "$3" "$4"',
             "test", str(LEGACY), flag, desktop, distro],
            capture_output=True, text=True,
        )

    def make_archive(self, desktop="niri", backend="anland-wayland",
                     binary=True, unit=True, leading_dot=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        archive = Path(tmp.name) / "rootfs.tar"
        contents = {
            "etc/droidspaces-desktop.conf":
                f"DESKTOP={desktop}\nDISPLAY_BACKEND={backend}\n".encode()
        }
        if binary:
            contents["usr/bin/niri-anland"] = b"ELF-NIRI"
        if unit:
            contents["etc/systemd/system/desktop-session.service"] = b"[Unit]\n"
        with tarfile.open(archive, "w") as tar:
            for name, data in contents.items():
                info = tarfile.TarInfo(("./" if leading_dot else "") + name)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        return archive

    def verify(self, archive, desktop="niri", backend="anland-wayland"):
        return subprocess.run(
            ["bash", "-c", 'source "$1"; verify_rootfs_desktop_tar "$2" "$3" "$4"',
             "test", str(VERIFY), str(archive), desktop, backend],
            capture_output=True, text=True,
        )

    def test_arch_niri_legacy_allowed(self):
        self.assertEqual(self.check_legacy("true", "niri", "Arch").returncode, 0)

    def test_mtk_niri_config_is_not_silently_overridden(self):
        # Both GPU profiles have the same desktop/systemd compatibility.
        for gpu in ("qualcomm-kgsl", "mediatek-mali"):
            with self.subTest(gpu=gpu):
                result = self.check_legacy("true", "niri", "Arch")
                self.assertEqual(result.returncode, 0)

    def test_unsupported_legacy_desktops_fail(self):
        for desktop, distro in (("niri", "Debian-13"), ("gnome", "Arch"),
                                ("kde-mobile", "Arch"), ("anland-next", "Arch")):
            with self.subTest(desktop=desktop, distro=distro):
                self.assertNotEqual(
                    self.check_legacy("true", desktop, distro).returncode, 0
                )

    def test_unmodified_legacy_allowed_combinations(self):
        for desktop, distro in (("kde", "Arch"), ("none", "Arch")):
            self.assertEqual(
                self.check_legacy("true", desktop, distro).returncode, 0
            )

    def test_valid_arch_niri_export_passes(self):
        self.assertEqual(self.verify(self.make_archive()).returncode, 0)

    def test_dot_prefixed_tar_members_are_supported(self):
        self.assertEqual(
            self.verify(self.make_archive(leading_dot=True)).returncode, 0
        )

    def test_requested_niri_cannot_be_cli(self):
        result = self.verify(self.make_archive("none", "x11", False, False))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Wrong RootFS desktop", result.stderr)

    def test_niri_without_binary_is_rejected(self):
        result = self.verify(self.make_archive(binary=False))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("niri-anland", result.stderr)

    def test_niri_without_unit_is_rejected(self):
        result = self.verify(self.make_archive(unit=False))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("desktop-session.service", result.stderr)

    def test_backend_mismatch_is_rejected(self):
        result = self.verify(self.make_archive(backend="x11"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Wrong RootFS backend", result.stderr)

    def test_cli_image_is_still_valid_as_cli(self):
        result = self.verify(
            self.make_archive("none", "x11", binary=False, unit=False),
            "none", "x11"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_native_builder_uses_preflight_and_export_verification(self):
        source = (ROOT / "build_rootfs-native.sh").read_text()
        self.assertIn(
            'validate_legacy_desktop "$ENABLE_systemd257" "$DESKTOP" "$PREFIX"',
            source
        )
        self.assertIn(
            'verify_rootfs_desktop_tar "$TEMP_TAR" "$DESKTOP" "$DISPLAY_BACKEND"',
            source
        )
        self.assertNotIn('DESKTOP="none"\n        DISPLAY_BACKEND="x11"', source)


if __name__ == "__main__":
    unittest.main()
