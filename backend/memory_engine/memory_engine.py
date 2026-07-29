"""
Cognitive Learning Engine (CLE)
Memory Engine

Version 0.6
"""

import json
from pathlib import Path
from typing import Any


class MemoryEngine:
    """Speichert und lädt Informationen aus einer JSON-Datei."""

    def __init__(self, storage_path: str = "memory.json") -> None:
        self.storage_path = Path(storage_path)

    def save(self, key: str, value: Any) -> None:
        """Speichert einen Wert unter einem Schlüssel."""
        memory = self._load_all()
        memory[key] = value
        self._write_all(memory)

    def load(self, key: str, default: Any = None) -> Any:
        """Lädt einen gespeicherten Wert."""
        memory = self._load_all()
        return memory.get(key, default)

    def delete(self, key: str) -> bool:
        """Löscht einen gespeicherten Wert."""
        memory = self._load_all()

        if key not in memory:
            return False

        del memory[key]
        self._write_all(memory)
        return True

    def exists(self, key: str) -> bool:
        """Prüft, ob ein Schlüssel gespeichert ist."""
        memory = self._load_all()
        return key in memory

    def get_all(self) -> dict[str, Any]:
        """Gibt den gesamten Speicher zurück."""
        return self._load_all()

    def clear(self) -> None:
        """Löscht den gesamten Speicher."""
        self._write_all({})

    def _load_all(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return {}

        try:
            content = self.storage_path.read_text(
                encoding="utf-8",
            )

            if not content.strip():
                return {}

            data = json.loads(content)

            if isinstance(data, dict):
                return data

            return {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_all(self, memory: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = json.dumps(
            memory,
            ensure_ascii=False,
            indent=4,
        )

        self.storage_path.write_text(
            content,
            encoding="utf-8",
        )