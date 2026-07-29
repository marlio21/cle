import tempfile
import unittest
from pathlib import Path

from memory_engine.memory_engine import MemoryEngine


class TestMemoryEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()

        storage_path = (
            Path(self.temporary_directory.name)
            / "memory.json"
        )

        self.memory = MemoryEngine(str(storage_path))

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_save_and_load_value(self) -> None:
        self.memory.save(
            "project_name",
            "Cognitive Learning Engine",
        )

        result = self.memory.load("project_name")

        self.assertEqual(
            result,
            "Cognitive Learning Engine",
        )

    def test_load_missing_value_returns_default(self) -> None:
        result = self.memory.load(
            "missing_key",
            "unknown",
        )

        self.assertEqual(result, "unknown")

    def test_exists_returns_true_for_saved_key(self) -> None:
        self.memory.save("language", "Python")

        self.assertTrue(
            self.memory.exists("language")
        )

    def test_delete_removes_value(self) -> None:
        self.memory.save("framework", "FastAPI")

        deleted = self.memory.delete("framework")

        self.assertTrue(deleted)
        self.assertFalse(
            self.memory.exists("framework")
        )

    def test_delete_missing_value_returns_false(self) -> None:
        deleted = self.memory.delete("missing_key")

        self.assertFalse(deleted)

    def test_get_all_returns_complete_memory(self) -> None:
        self.memory.save("language", "Python")
        self.memory.save("framework", "FastAPI")

        result = self.memory.get_all()

        self.assertEqual(
            result,
            {
                "language": "Python",
                "framework": "FastAPI",
            },
        )

    def test_clear_removes_all_values(self) -> None:
        self.memory.save("language", "Python")
        self.memory.save("framework", "FastAPI")

        self.memory.clear()

        self.assertEqual(
            self.memory.get_all(),
            {},
        )


if __name__ == "__main__":
    unittest.main()