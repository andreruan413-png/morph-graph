from collections import defaultdict


class DecisionLearning:
    """
    Aprende a confiabilidade das evidências usadas nas decisões.

    A magnitude bruta de um score não determina sozinha a importância
    da evidência. Cada decisão é normalizada antes de contribuir para
    o aprendizado.

    Resultado:
        evidência frequentemente presente em decisões bem-sucedidas
        -> peso positivo

        evidência frequentemente presente em decisões malsucedidas
        -> peso negativo
    """

    EVIDENCE_KEYS = (
        "context",
        "trajectory",
        "graph",
        "failure",
        "transition",
        "learned",
    )

    def __init__(self, graph, learning_rate=0.1):
        self.graph = graph
        self.learning_rate = float(learning_rate)

    def _decisions(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node.get("type") == "decision"
        ]

    def _normalized_evidence(self, scores):
        """
        Converte os scores brutos em proporções.

        Assim, context=100 não vale automaticamente 10x mais
        que graph=10.
        """
        values = {}

        for key in self.EVIDENCE_KEYS:
            try:
                values[key] = float(scores.get(key, 0.0))
            except (TypeError, ValueError):
                values[key] = 0.0

        magnitude = sum(abs(value) for value in values.values())

        if magnitude == 0.0:
            return {key: 0.0 for key in self.EVIDENCE_KEYS}

        return {
            key: values[key] / magnitude
            for key in self.EVIDENCE_KEYS
        }

    def _learning_statistics(self):
        """
        Calcula estatísticas de sucesso/falha por evidência.
        """
        statistics = {
            key: {
                "success": 0.0,
                "failure": 0.0,
                "observations": 0.0,
            }
            for key in self.EVIDENCE_KEYS
        }

        for decision in self._decisions():
            data = decision.get("data", {})
            outcome = data.get("outcome")

            if outcome not in ("success", "failure"):
                continue

            normalized = self._normalized_evidence(
                data.get("scores", {})
            )

            for key in self.EVIDENCE_KEYS:
                value = normalized[key]

                if value == 0.0:
                    continue

                statistics[key]["observations"] += 1.0

                if outcome == "success":
                    statistics[key]["success"] += abs(value)
                else:
                    statistics[key]["failure"] += abs(value)

        return statistics

    def learned_weights(self):
        """
        Aprende um peso entre -1 e +1 para cada evidência.

        +1  -> evidência associada fortemente a sucesso
         0  -> evidência sem sinal claro
        -1  -> evidência associada fortemente a falha
        """
        statistics = self._learning_statistics()
        weights = {}

        for key, stats in statistics.items():
            success = stats["success"]
            failure = stats["failure"]
            total = success + failure

            if total == 0.0:
                weights[key] = 0.0
                continue

            weights[key] = (success - failure) / total

        return weights

    def reliability(self):
        """
        Retorna informações detalhadas sobre a confiabilidade
        de cada evidência.
        """
        statistics = self._learning_statistics()
        weights = self.learned_weights()

        result = {}

        for key in self.EVIDENCE_KEYS:
            stats = statistics[key]
            observations = stats["observations"]

            if observations == 0.0:
                success_rate = 0.0
            else:
                success_rate = (
                    stats["success"]
                    / (
                        stats["success"]
                        + stats["failure"]
                    )
                    if (
                        stats["success"]
                        + stats["failure"]
                    ) > 0
                    else 0.0
                )

            result[key] = {
                "success": stats["success"],
                "failure": stats["failure"],
                "observations": observations,
                "success_rate": success_rate,
                "weight": weights[key],
            }

        return result

    def score(self, decision_score):
        """
        Calcula o score aprendido de uma nova decisão.

        Primeiro normaliza as evidências da decisão.
        Depois aplica os pesos aprendidos.
        """
        weights = self.learned_weights()

        normalized = self._normalized_evidence(
            decision_score.as_dict()
        )

        total = 0.0

        for key in self.EVIDENCE_KEYS:
            total += normalized[key] * weights.get(key, 0.0)

        return total

    def explain(self, decision_score):
        """
        Explica como cada evidência contribuiu para a decisão.
        """
        weights = self.learned_weights()
        normalized = self._normalized_evidence(
            decision_score.as_dict()
        )

        contributions = {}

        for key in self.EVIDENCE_KEYS:
            value = normalized[key]
            weight = weights.get(key, 0.0)

            contributions[key] = {
                "normalized_value": value,
                "weight": weight,
                "contribution": value * weight,
            }

        return contributions
