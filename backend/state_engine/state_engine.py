"""
Cognitive Learning Engine (CLE)
State Engine

Version 0.5.1
"""

import ast
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


ENTRY_POINT_FILENAMES = {
    "main.py",
    "run.py",
    "app.py",
    "server.py",
    "manage.py",
    "index.py",
    "index.js",
    "index.ts",
    "server.js",
    "server.ts",
    "main.js",
    "main.ts",
}


ARCHITECTURE_DIRECTORIES = {
    "backend",
    "frontend",
    "api",
    "services",
    "controllers",
    "models",
    "views",
    "templates",
    "static",
    "src",
    "tests",
    "common",
    "orchestrator",
}


@dataclass
class ProjectState:
    project_name: str
    exists: bool
    language: str
    framework: str
    architecture: str
    file_count: int
    directories: list[str]
    files: list[str]
    modules: list[str]
    test_files: list[str]
    entry_points: list[str]


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
                architecture="unknown",
                file_count=0,
                directories=[],
                files=[],
                modules=[],
                test_files=[],
                entry_points=[],
            )

        language_counts: dict[str, int] = {}
        directories: list[str] = []
        files: list[str] = []
        modules: list[str] = []
        test_files: list[str] = []
        entry_points: list[str] = []

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

            is_test_file = self._is_test_file(path)

            if is_test_file:
                test_files.append(relative_file)

            if not is_test_file and self._is_entry_point(path):
                entry_points.append(relative_file)

        detected_language = self._detect_primary_language(
            language_counts
        )

        framework = self._detect_framework(project)

        architecture = self._detect_architecture(
            project=project,
            directories=directories,
            modules=modules,
        )

        return ProjectState(
            project_name=project.name,
            exists=True,
            language=detected_language,
            framework=framework,
            architecture=architecture,
            file_count=len(files),
            directories=sorted(directories),
            files=sorted(files),
            modules=sorted(set(modules)),
            test_files=sorted(test_files),
            entry_points=sorted(entry_points),
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

        try:
            return any(
                child.suffix.lower() == ".py"
                for child in path.iterdir()
                if child.is_file()
            )
        except (OSError, PermissionError):
            return False

    def _is_test_file(self, path: Path) -> bool:
        filename = path.name.lower()

        return (
            filename.startswith("test_")
            or filename.endswith("_test.py")
            or ".test." in filename
            or ".spec." in filename
        )

    def _is_entry_point(self, path: Path) -> bool:
        filename = path.name.lower()

        if filename in ENTRY_POINT_FILENAMES:
            return True

        if path.suffix.lower() != ".py":
            return False

        return self._has_python_main_guard(path)

    def _has_python_main_guard(self, path: Path) -> bool:
        try:
            content = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
            syntax_tree = ast.parse(content)
        except (OSError, SyntaxError):
            return False

        for node in ast.walk(syntax_tree):
            if not isinstance(node, ast.If):
                continue

            if self._is_main_guard_comparison(node.test):
                return True

        return False

    def _is_main_guard_comparison(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.Compare):
            return False

        if len(node.ops) != 1:
            return False

        if not isinstance(node.ops[0], ast.Eq):
            return False

        if len(node.comparators) != 1:
            return False

        left = node.left
        right = node.comparators[0]

        return (
            self._is_name_variable(left)
            and self._is_main_string(right)
        ) or (
            self._is_main_string(left)
            and self._is_name_variable(right)
        )

    def _is_name_variable(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Name)
            and node.id == "__name__"
        )

    def _is_main_string(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Constant)
            and node.value == "__main__"
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

    def _detect_architecture(
        self,
        project: Path,
        directories: list[str],
        modules: list[str],
    ) -> str:
        top_level_directories = {
            Path(directory).parts[0].lower()
            for directory in directories
            if Path(directory).parts
        }

        module_names = {
            module.lower()
            for module in modules
        }

        if {"frontend", "backend"}.issubset(
            top_level_directories
        ):
            return "Full-stack"

        top_level_files = {
            path.name.lower()
            for path in project.iterdir()
            if path.is_file()
        }

        if "manage.py" in top_level_files:
            return "Django MVC"

        if {
            "controllers",
            "models",
            "views",
        }.issubset(top_level_directories):
            return "MVC"

        cle_modules = {
            "state_engine",
            "memory_engine",
            "prediction_engine",
            "option_engine",
            "evaluation_engine",
            "learning_engine",
            "orchestrator",
        }

        if len(
            cle_modules.intersection(top_level_directories)
        ) >= 3:
            return "Modular Engine Architecture"

        if len(cle_modules.intersection(module_names)) >= 3:
            return "Modular Engine Architecture"

        architecture_matches = (
            top_level_directories.intersection(
                ARCHITECTURE_DIRECTORIES
            )
        )

        if "src" in architecture_matches:
            return "Source-based"

        if "api" in architecture_matches:
            return "API-based"

        if len(module_names) >= 2:
            return "Modular"

        if modules:
            return "Single Module"

        return "Flat"