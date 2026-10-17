"""Fast offline checks for GPU and desktop expansion in the batch planner."""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/ci/build-batch-matrix.sh"

BASE_FLAGS = {
    "DISTRO_ARCH": "true",
    "DISTRO_DEBIAN_13": "false",
    "DISTRO_UBUNTU_24": "false",
    "DISTRO_UBUNTU_25": "false",
    "DISTRO_UBUNTU_26": "false",
    "DISTRO_FEDORA_43": "false",
    "DISTRO_FEDORA_44": "false",
    "DESKTOP_NONE": "false",
    "DESKTOP_KDE": "false",
    "DESKTOP_KDE_MOBILE": "false",
    "DESKTOP_GNOME": "false",
    "DESKTOP_ANLAND_NEXT": "false",
    "DESKTOP_NIRI": "true",
    "GPU_QUALCOMM": "true",
    "GPU_MEDIATEK": "true",
    "KDE_BACKEND": "anland-wayland",
}


@unittest.skipUnless(shutil.which("jq"), "jq is required by the planner")
class GpuBatchMatrixTests(unittest.TestCase):
    def plan(self, **settings):
        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp) / "output"
            summary = pathlib.Path(tmp) / "summary"
            env = dict(os.environ)
            env.update(BASE_FLAGS)
            env.update(settings)
            env["GITHUB_OUTPUT"] = str(output)
            env["GITHUB_STEP_SUMMARY"] = str(summary)
            result = subprocess.run(
                ["bash", str(SCRIPT)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                return result, []
            line = next(
                (line for line in output.read_text().splitlines()
                 if line.startswith("matrix=")), None
            )
            self.assertIsNotNone(line, result.stdout)
            return result, json.loads(line[7:])["include"]

    def test_default_arch_niri_builds_both_gpus(self):
        result, combinations = self.plan()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(combinations), 2)
        self.assertEqual(
            {item["gpu"] for item in combinations},
            {"qualcomm-kgsl", "mediatek-mali"},
        )
        self.assertTrue(all(item["target"] == "Arch" and
                            item["desktop"] == "niri" for item in combinations))

    def test_qualcomm_only(self):
        result, combinations = self.plan(GPU_MEDIATEK="false")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(combinations), 1)
        self.assertEqual(combinations[0]["gpu"], "qualcomm-kgsl")

    def test_mediatek_only(self):
        result, combinations = self.plan(GPU_QUALCOMM="false")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(combinations), 1)
        self.assertEqual(combinations[0]["gpu"], "mediatek-mali")

    def test_no_gpus_fails_before_build(self):
        result, combinations = self.plan(GPU_QUALCOMM="false", GPU_MEDIATEK="false")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Select at least one GPU", result.stderr)
        self.assertEqual(combinations, [])

    def test_mixed_desktops_multiply_profiles_and_skip_unsupported(self):
        result, combos = self.plan(
            DISTRO_DEBIAN_13="true", DESKTOP_KDE_MOBILE="true"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(combos), 6)
        self.assertEqual(
            sum(item["target"] == "Arch" for item in combos), 4
        )
        self.assertEqual(
            sum(item["target"] == "Debian-13" for item in combos), 2
        )
        self.assertEqual(
            len({(x["target"], x["desktop"], x["gpu"]) for x in combos}), 6
        )

    def test_legacy_systemd257_arch_niri_keeps_gpu_variants(self):
        result, items = self.plan(LEGACY_SYSTEMD257="true")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(items), 2)
        self.assertTrue(all(item["target"] == "Arch" and
                            item["desktop"] == "niri" for item in items))

    def test_legacy_systemd257_rejects_unvalidated_desktops(self):
        result, items = self.plan(LEGACY_SYSTEMD257="true",
                                  DESKTOP_GNOME="true")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("systemd 257 is not supported for gnome", result.stderr)
        self.assertEqual(items, [])

    def test_kde_x11_backend_is_preserved_for_both_gpus(self):
        result, combos = self.plan(
            DESKTOP_NIRI="false", DESKTOP_KDE="true", KDE_BACKEND="x11"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(combos), 2)
        self.assertTrue(all(x["backend"] == "x11" for x in combos))


if __name__ == "__main__":
    unittest.main()
