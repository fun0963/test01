import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXTSTAT_PATH = os.path.join(REPO_ROOT, "txtstat.py")


def run_txtstat(path):
    return subprocess.run(
        [sys.executable, TXTSTAT_PATH, path],
        capture_output=True,
        text=True,
    )


class TestTxtstatCLI(unittest.TestCase):
    def test_normal_file(self):
        content = "hello world\nsecond line\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            path = f.name

        try:
            result = run_txtstat(path)
        finally:
            os.remove(path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "lines=2 words=4 chars=24")
        self.assertEqual(result.stderr, "")

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            path = f.name

        try:
            result = run_txtstat(path)
        finally:
            os.remove(path)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "lines=0 words=0 chars=0")

    def test_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "does-not-exist.txt")
            result = run_txtstat(path)

        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
