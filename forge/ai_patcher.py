from pathlib import Path
import shutil


class AIPatcher:
    def __init__(self, backup_dir="reports/ai_backups"):
        self.backup_dir = Path(backup_dir)

    def apply(self, file_path, replacement):
        target = Path(file_path)

        if not target.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {target}"
            )

        self.backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup = (
            self.backup_dir
            / f"{target.name}.bak"
        )

        shutil.copy2(target, backup)

        target.write_text(
            replacement,
            encoding="utf-8",
        )

        return {
            "file": str(target),
            "backup": str(backup),
            "changed": True,
        }

    def restore(self, file_path):
        target = Path(file_path)

        backup = (
            self.backup_dir
            / f"{target.name}.bak"
        )

        if not backup.exists():
            raise FileNotFoundError(
                f"Backup não encontrado: {backup}"
            )

        shutil.copy2(backup, target)

        return {
            "file": str(target),
            "restored": True,
        }
