from pathlib import Path
import subprocess

from forge.ai_agent import AIRepairAgent
from forge.ai_patcher import AIPatcher


class AIRepairLoop:
    def __init__(self, model=None, max_attempts=5):
        self.agent = AIRepairAgent(model=model)
        self.patcher = AIPatcher()
        self.max_attempts = max_attempts

    def run_tests(self, test_command):
        result = subprocess.run(
            test_command,
            shell=True,
            text=True,
            capture_output=True,
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        ).strip()

        return result.returncode == 0, output

    def repair(
        self,
        file_path,
        test_command,
        problem="",
    ):
        target = Path(file_path)

        if not target.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {target}"
            )

        source = target.read_text(
            encoding="utf-8"
        )

        history = []

        for attempt in range(1, self.max_attempts + 1):
            print(f"\n=== TENTATIVA {attempt} ===")

            passed, output = self.run_tests(
                test_command
            )

            if passed:
                print("TESTES PASSARAM.")
                return {
                    "success": True,
                    "attempts": attempt - 1,
                    "history": history,
                }

            print("TESTES FALHARAM.")

            analysis = self.agent.analyze(
                source=source,
                error=problem + "\n" + output,
                tests=test_command,
            )

            replacement = analysis.get(
                "replacement"
            )

            if not replacement:
                raise RuntimeError(
                    "A IA não retornou replacement."
                )

            backup = self.patcher.apply(
                target,
                replacement,
            )

            history.append({
                "attempt": attempt,
                "diagnosis": analysis.get(
                    "diagnosis", ""
                ),
                "confidence": analysis.get(
                    "confidence", 0
                ),
                "reason": analysis.get(
                    "reason", ""
                ),
                "backup": backup["backup"],
            })

            source = target.read_text(
                encoding="utf-8"
            )

        passed, output = self.run_tests(
            test_command
        )

        return {
            "success": passed,
            "attempts": self.max_attempts,
            "final_output": output,
            "history": history,
        }
