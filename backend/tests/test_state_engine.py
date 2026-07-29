import tempfile
import unittest
from pathlib import Path

from state_engine.state_engine import StateEngine


class TestStateEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = StateEngine()

    def test_existing_python_fastapi_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)

            (project / "requirements.txt").write_text(
                "fastapi\nuvicorn\n",
                encoding="utf-8",
            )

            module_directory = project / "state_engine"
            module_directory.mkdir()

            (module_directory / "__init__.py").write_text(
                "",
                encoding="utf-8",
            )

            (module_directory / "engine.py").write_text(
                "class Example:\n    pass\n",
                encoding="utf-8",
            )

            state = self.engine.analyze(str(project))

            self.assertTrue(state.exists)
            self.assertEqual(state.language, "Python")
            self.assertEqual(state.framework, "FastAPI")
            self.assertGreaterEqual(state.file_count, 3)
            self.assertIn("state_engine", state.modules)

    def test_missing_project(self) -> None:
        missing_path = Path("path-that-does-not-exist")

        state = self.engine.analyze(str(missing_path))

        self.assertFalse(state.exists)
        self.assertEqual(state.language, "unknown")
        self.assertEqual(state.framework, "unknown")
        self.assertEqual(state.file_count, 0)
        self.assertEqual(state.modules, [])
        self.assertEqual(state.test_files, [])


if __name__ == "__main__":
    unittest.main()