import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(cmd):
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT / 'src'}" + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)


class TestEntrypoints(unittest.TestCase):
    def test_module_help(self):
        result = _run([sys.executable, "-m", "plex_music_hygiene.cli", "--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Plex Music Toolkit", result.stdout)

    def test_script_help(self):
        result = _run([sys.executable, "scripts/plex_music_toolkit.py", "--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Plex Music Toolkit", result.stdout)

    def test_posix_wrapper_help_when_available(self):
        wrapper = ROOT / "bin" / "plexh"
        if os.name == "nt" or not wrapper.exists():
            self.skipTest("POSIX wrapper not applicable")
        result = _run([str(wrapper), "--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Plex Music Toolkit", result.stdout)


if __name__ == "__main__":
    unittest.main()
