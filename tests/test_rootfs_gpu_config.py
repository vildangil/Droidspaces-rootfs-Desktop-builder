"""Check generated DroidSpaces import permissions for GPU profiles."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts/lib/rootfs-config.sh"


class ImportedGpuSettingsTests(unittest.TestCase):
    def generate(self, desktop, backend, gpu_mesa):
        with tempfile.TemporaryDirectory() as work:
            config = Path(work) / "container.config"
            cmd = (
                'source "$1"; '
                'write_rootfs_config "$2" "$3" "$4" none false "$5" false'
            )
            subprocess.run(
                ["bash", "-c", cmd, "_", str(MODULE), str(config),
                 desktop, backend, "true" if gpu_mesa else "false"],
                check=True, capture_output=True, text=True, cwd=ROOT,
            )
            return dict(line.split("=", 1) for line in
                        config.read_text().splitlines() if "=" in line)

    def test_mediatek_niri_enables_gpu_only_for_anland(self):
        data = self.generate("niri", "anland-wayland", False)
        self.assertEqual(data["enable_gpu_mode"], "1")
        self.assertEqual(data["enable_anland"], "1")
        self.assertNotIn("enable_hw_access", data)

    def test_qualcomm_niri_keeps_gpu_access(self):
        data = self.generate("niri", "anland-wayland", True)
        self.assertEqual(data["enable_gpu_mode"], "1")
        self.assertEqual(data["enable_anland"], "1")

    def test_anland_with_no_custom_mesa_still_needs_gpu(self):
        for desktop in ("kde", "kde-mobile", "gnome", "anland-next"):
            with self.subTest(desktop=desktop):
                data = self.generate(desktop, "anland-wayland", False)
                self.assertEqual(data["enable_gpu_mode"], "1")
                self.assertEqual(data["enable_anland"], "1")

    def test_cli_container_remains_gpu_free(self):
        data = self.generate("none", "x11", False)
        self.assertEqual(data["enable_gpu_mode"], "0")
        self.assertEqual(data["enable_anland"], "0")

    def test_kde_x11_preserves_explicit_gpu_choice(self):
        self.assertEqual(
            self.generate("kde", "x11", False)["enable_gpu_mode"], "0"
        )
        self.assertEqual(
            self.generate("kde", "x11", True)["enable_gpu_mode"], "1"
        )


if __name__ == "__main__":
    unittest.main()
