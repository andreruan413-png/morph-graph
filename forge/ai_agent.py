import json
import os
import urllib.request

class AIRepairAgent:
    def __init__(self, model=None):
        self.model = model or os.environ.get("MORPH_GRAPH_MODEL")
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def _request(self, prompt):
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada.")
        if not self.model:
            raise RuntimeError("MORPH_GRAPH_MODEL não configurado.")

        data = json.dumps({
            "model": self.model,
            "input": prompt
        }).encode()

        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.api_key
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read().decode())

        if "output_text" in result:
            return result["output_text"]

        out = []
        for item in result.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    out.append(content.get("text", ""))

        return "\n".join(out).strip()

    def analyze(self, source, error="", tests=""):
        prompt = "\n".join([
            "Você é o agente de reparo do Morph-Graph.",
            "Analise o código Python e proponha uma correção mínima.",
            "",
            "CODIGO:",
            source,
            "",
            "TESTES:",
            tests,
            "",
            "ERRO:",
            error,
            "",
            "Responda somente JSON válido com:",
            "diagnosis, confidence, replacement, reason."
        ])

        raw = self._request(prompt)
        return json.loads(raw)
