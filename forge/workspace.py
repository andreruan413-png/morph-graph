from pathlib import Path
import shutil
import tempfile


class ForgeWorkspace:
    """Ambiente isolado para analisar e modificar um projeto."""

    def __init__(self, repository):
        self.repository = Path(repository).resolve()
        self.root = None

    def create(self):
        if not self.repository.exists():
            raise FileNotFoundError(
                f"repository not found: {self.repository}"
            )

        if not self.repository.is_dir():
            raise ValueError(
                f"repository is not a directory: {self.repository}"
            )

        self.root = Path(
            tempfile.mkdtemp(prefix="morph_forge_")
        )

        destination = self.root / self.repository.name

        shutil.copytree(
            self.repository,
            destination,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".venv",
                "venv",
            ),
        )

        return destination

    def path(self, relative_path):
        if self.root is None:
            raise RuntimeError(
                "workspace has not been created"
            )

        target = self.root / self.repository.name / relative_path
        return target

    def cleanup(self):
        if self.root is not None and self.root.exists():
            shutil.rmtree(self.root)
            self.root = None
