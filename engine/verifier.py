import subprocess
import sys
import tempfile
import os


class VerificationResult:
    def __init__(self, success, score, stdout="", stderr="", reason=""):
        self.success = success
        self.score = float(score)
        self.stdout = stdout
        self.stderr = stderr
        self.reason = reason

    def as_dict(self):
        return {
            "success": self.success,
            "score": self.score,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "reason": self.reason
        }


def verify_python_code(code, timeout=3):
    """
    Executa código Python em um arquivo temporário.

    Sucesso:
        processo termina com código 0.

    Falha:
        erro de execução, erro de sintaxe ou timeout.
    """

    path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as file:
            file.write(code)
            path = file.name

        try:
            result = subprocess.run(
                [sys.executable, path],
                capture_output=True,
                text=True,
                timeout=timeout
            )

        except subprocess.TimeoutExpired:
            return VerificationResult(
                success=False,
                score=0.0,
                reason="execução excedeu o limite de tempo"
            )

        if result.returncode == 0:
            return VerificationResult(
                success=True,
                score=1.0,
                stdout=result.stdout,
                stderr=result.stderr,
                reason="código executado com sucesso"
            )

        return VerificationResult(
            success=False,
            score=0.0,
            stdout=result.stdout,
            stderr=result.stderr,
            reason="código terminou com erro"
        )

    finally:
        if path and os.path.exists(path):
            os.remove(path)
