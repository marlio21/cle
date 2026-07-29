"""
Cognitive Learning Engine (CLE)
State Engine

Version 0.4
"""

from dataclasses import dataclass
from pathlib import Path


LANGUAGE_BY_EXTENSION = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".cs": "C#",
}


IGNORED_DIRECTORIES = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
}


@dataclass
class ProjectState:
    project_name: str
    exists: bool
    language: str
    framework: str
    file_count: int
    directories: list[str]
    files: list[str]
    modules: list[str]
    test_files: list[str]


class StateEngine:
    """Analysiert ein Projekt und erzeugt einen strukturierten State."""

    def analyze(self, project_path: str) -> ProjectState:
        project = Path(project_path).resolve()

        if not project.exists():
            return ProjectState(
                project_name=project.name,
                exists=False,
                language="unknown",
                framework="unknown",
                file_count=0,
                directories=[],
                files=[],
                modules=[],
                test_files=[],
            )

        language_counts: dict[str, int] = {}
        directories: list[str] = []
        files: list[str] = []
        modules: list[str] = []
        test_files: list[str] = []

        for path in project.rglob("*"):
            if self._is_ignored(path):
                continue

            relative_path = path.relative_to(project)

            if path.is_dir():
                directories.append(str(relative_path))

                if self._is_module_directory(path):
                    modules.append(path.name)

                continue

            if not path.is_file():
                continue

            relative_file = str(relative_path)
            files.append(relative_file)

            language = LANGUAGE_BY_EXTENSION.get(path.suffix.lower())

            if language:
                language_counts[language] = (
                    language_counts.get(language, 0) + 1
                )

            if self._is_test_file(path):
                test_files.append(relative_file)

        detected_language = self._detect_primary_language(
            language_counts
        )

        framework = self._detect_framework(project)

        return ProjectState(
            project_name=project.name,
            exists=True,
            language=detected_language,
            framework=framework,
            file_count=len(files),
            directories=sorted(directories),
            files=sorted(files),
            modules=sorted(set(modules)),
            test_files=sorted(test_files),
        )

    def _is_ignored(self, path: Path) -> bool:
        return any(
            part in IGNORED_DIRECTORIES
            for part in path.parts
        )

    def _is_module_directory(self, path: Path) -> bool:
        if path.name.startswith("."):
            return False

        if path.name in IGNORED_DIRECTORIES:
            return False

        return any(
            child.suffix == ".py"
            for child in path.iterdir()
            if child.is_file()
        )

    def _is_test_file(self, path: Path) -> bool:
        filename = path.name.lower()

        return (
            filename.startswith("test_")
            or filename.endswith("_test.py")
            or ".test." in filename
            or ".spec." in filename
        )

    def _detect_primary_language(
        self,
        language_counts: dict[str, int],
    ) -> str:
        if not language_counts:
            return "unknown"

        return max(
            language_counts,
            key=language_counts.get,
        )

    def _detect_framework(self, project: Path) -> str:
        package_json = project / "package.json"

        if package_json.exists():
            content = package_json.read_text(
                encoding="utf-8",
                errors="ignore",
            ).lower()

            if '"next"' in content:
                return "Next.js"

            if '"react"' in content:
                return "React"

            if '"vue"' in content:
                return "Vue"

            if '"express"' in content:
                return "Express"

            return "Node.js"

        python_dependency_files = [
            project / "requirements.txt",
            project / "pyproject.toml",
            project / "pipfile",
        ]

        dependency_content = ""

        for dependency_file in python_dependency_files:
            if dependency_file.exists():
                dependency_content += dependency_file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).lower()

        if "fastapi" in dependency_content:
            return "FastAPI"

        if "django" in dependency_content:
            return "Django"

        if "flask" in dependency_content:
            return "Flask"

        if dependency_content:
            return "Python project"

        return "unknown"