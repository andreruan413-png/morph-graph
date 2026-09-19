import subprocess
import sys
import tempfile
import os


class ProblemResult:
    def __init__(
        self,
        success,
        score,
        passed,
        total,
        stdout="",
        stderr="",
        reason=""
    ):
        self.success = success
        self.score = float(score)
        self.passed = passed
        self.total = total
        self.stdout = stdout
        self.stderr = stderr
        self.reason = reason

    def as_dict(self):
        return {
            "success": self.success,
            "score": self.score,
            "passed": self.passed,
            "total": self.total,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "reason": self.reason,
        }


def evaluate_problem(code, tests, timeout=3):
    """
    Avalia o código candidato.

    Aceita:
      1. testes no formato TEST:
         TEST: calcular(10, 3) == 13
         TEST: assert calcular(20, 5) == 25

      2. script Python completo que recebe o caminho do candidato
         em sys.argv[1].
    """

    if not tests or not tests.strip():
        raise ValueError("Nenhum teste encontrado.")

    candidate_path = None
    runner_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as candidate_file:
            candidate_file.write(code)
            candidate_path = candidate_file.name

        # Formato TEST:
        test_lines = [
            line.strip()[len("TEST:"):].strip()
            for line in tests.splitlines()
            if line.strip().startswith("TEST:")
        ]

        if test_lines:
            test_blocks = []

            for index, expression in enumerate(test_lines, start=1):
                assertion = (
                    expression
                    if expression.startswith("assert ")
                    else f"assert {expression}"
                )

                test_blocks.append(
                    f"""
try:
    {assertion}
    passed += 1
    print("TEST_PASS:{index}")
except AssertionError as exc:
    print("TEST_FAIL:{index}", exc)
except Exception as exc:
    print("TEST_ERROR:{index}", type(exc).__name__, exc)
""".replace("{index}", str(index))
                )

            runner = f"""
import importlib.util

passed = 0

spec = importlib.util.spec_from_file_location(
    "candidate",
    {candidate_path!r}
)

candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)

{"".join(test_blocks)}

total = {len(test_lines)}
print(f"TEST_SUMMARY:{{passed}}/{{total}}")
"""

        else:
            # Script Python completo.
            runner = tests

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as runner_file:
            runner_file.write(runner)
            runner_path = runner_file.name

        process = subprocess.run(
            [sys.executable, runner_path, candidate_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        stdout = process.stdout
        stderr = process.stderr

        # Script completo: sucesso = processo terminou sem erro.
        if not test_lines:
            success = process.returncode == 0

            passed = 0
            total = 0

            for line in stdout.splitlines():
                if line.startswith("TEST_PASS:"):
                    passed += 1
                elif line.startswith("TEST_FAIL:") or line.startswith("TEST_ERROR:"):
                    total += 1

            if passed or total:
                total = max(total, passed)
            else:
                total = 1 if success else 0
                passed = 1 if success else 0

            score = passed / total if total else (1.0 if success else 0.0)

            return ProblemResult(
                success=success,
                score=score,
                passed=passed,
                total=total,
                stdout=stdout,
                stderr=stderr,
                reason=(
                    "Todos os testes passaram."
                    if success
                    else "O script de testes falhou."
                ),
            )

        # Formato TEST:
        passed = sum(
            1 for line in stdout.splitlines()
            if line.startswith("TEST_PASS:")
        )

        total = len(test_lines)
        success = process.returncode == 0 and passed == total
        score = passed / total if total else 0.0

        return ProblemResult(
            success=success,
            score=score,
            passed=passed,
            total=total,
            stdout=stdout,
            stderr=stderr,
            reason=(
                "Todos os testes passaram."
                if success
                else f"{passed}/{total} testes passaram."
            ),
        )

    finally:
        for path in (candidate_path, runner_path):
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass
