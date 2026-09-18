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
            "reason": self.reason
        }


def evaluate_problem(
    code,
    tests,
    timeout=3
):
    """
    Executa o código candidato contra todos os testes.

    Cada teste deve estar em uma linha começando com TEST:.

    Exemplos:

    TEST: resolver(3, 2) == (5, 1)
    TEST: assert resolver(10, 4) == (14, 6)
    """

    test_lines = [
        line.strip()[len("TEST:"):].strip()
        for line in tests.splitlines()
        if line.strip().startswith("TEST:")
    ]

    if not test_lines:
        raise ValueError(
            "Nenhum teste encontrado."
        )

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

        test_blocks = []

        for index, expression in enumerate(
            test_lines,
            start=1
        ):

            if expression.startswith("assert "):
                assertion = expression
            else:
                assertion = f"assert {expression}"

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
""".replace(
                    "{index}",
                    str(index)
                )
            )

        runner = f"""
import importlib.util

spec = importlib.util.spec_from_file_location(
    "candidate",
    {candidate_path!r}
)

candidate = importlib.util.module_from_spec(spec)

spec.loader.exec_module(candidate)

globals().update(
    {{
        name: getattr(candidate, name)
        for name in dir(candidate)
        if not name.startswith("_")
    }}
)

passed = 0
total = {len(test_lines)}

{chr(10).join(test_blocks)}

print(f"RESULT:{{passed}}/{{total}}")
"""

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as runner_file:

            runner_file.write(runner)
            runner_path = runner_file.name

        env = os.environ.copy()

        env.pop(
            "PYTHONOPTIMIZE",
            None
        )

        result = subprocess.run(
            [
                sys.executable,
                runner_path
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )

        stdout = result.stdout
        stderr = result.stderr

        passed = stdout.count(
            "TEST_PASS:"
        )

        total = len(test_lines)

        score = (
            passed / total
            if total
            else 0.0
        )

        success = (
            passed == total
        )

        reason = (
            f"{passed}/{total} testes passaram"
        )

        if stderr.strip():
            reason += (
                f" | stderr: "
                f"{stderr.strip()}"
            )

        return ProblemResult(
            success=success,
            score=score,
            passed=passed,
            total=total,
            stdout=stdout,
            stderr=stderr,
            reason=reason
        )

    except subprocess.TimeoutExpired:

        return ProblemResult(
            success=False,
            score=0.0,
            passed=0,
            total=len(test_lines),
            stdout="",
            stderr="timeout",
            reason=(
                "execução excedeu "
                "o limite de tempo"
            )
        )

    except Exception as exc:

        return ProblemResult(
            success=False,
            score=0.0,
            passed=0,
            total=len(test_lines),
            stdout="",
            stderr=str(exc),
            reason=(
                "erro ao avaliar candidato: "
                f"{type(exc).__name__}: {exc}"
            )
        )

    finally:

        if (
            candidate_path
            and os.path.exists(candidate_path)
        ):
            os.remove(candidate_path)

        if (
            runner_path
            and os.path.exists(runner_path)
        ):
            os.remove(runner_path)
