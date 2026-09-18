from collections import defaultdict

from engine.structure import structural_profile, structural_similarity
from engine.decision_learning import DecisionLearning


class ContextDecisionLearning:
    """
    Aprende a confiabilidade das evidências considerando
    o contexto estrutural do código.

    Experiências estruturalmente semelhantes influenciam
    mais a decisão atual.
    """

    def __init__(
        self,
        graph,
        similarity_threshold=0.5,
    ):
        self.graph = graph
        self.similarity_threshold = float(similarity_threshold)
        self.global_learning = DecisionLearning(graph)

    def _decisions(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node.get("type") == "decision"
        ]

    def _experience_code(self, experience):
        data = experience.get("data", {})

        source_code = data.get("source_code")
        if source_code:
            return source_code

        solution_node = data.get("solution_node")

        if solution_node:
            node = self.graph.nodes.get(solution_node)

            if node:
                return node.get("data", {}).get("code", "")

        return ""

    def _decision_code(self, decision):
        data = decision.get("data", {})

        source_code = data.get("source_code")

        if source_code:
            return source_code

        problem_id = data.get("problem_id")

        if problem_id:
            problem = self.graph.nodes.get(problem_id)

            if problem:
                return problem.get("data", {}).get("code", "")

        return ""

    def _similarity(self, current_code, decision):
        previous_code = self._decision_code(decision)

        if not previous_code:
            return 0.0

        try:
            current_profile = structural_profile(current_code)
            previous_profile = structural_profile(previous_code)

            return float(
                structural_similarity(
                    current_profile,
                    previous_profile,
                )
            )

        except Exception:
            return 0.0

    def _normalized(self, scores):
        values = {}

        for key in DecisionLearning.EVIDENCE_KEYS:
            try:
                values[key] = float(
                    scores.get(key, 0.0)
                )
            except (TypeError, ValueError):
                values[key] = 0.0

        magnitude = sum(
            abs(value)
            for value in values.values()
        )

        if magnitude == 0.0:
            return {
                key: 0.0
                for key in DecisionLearning.EVIDENCE_KEYS
            }

        return {
            key: values[key] / magnitude
            for key in DecisionLearning.EVIDENCE_KEYS
        }

    def learned_weights(self, current_code):
        """
        Aprende pesos usando apenas decisões suficientemente
        semelhantes ao contexto atual.
        """

        statistics = {
            key: {
                "success": 0.0,
                "failure": 0.0,
                "similarity": 0.0,
            }
            for key in DecisionLearning.EVIDENCE_KEYS
        }

        for decision in self._decisions():
            data = decision.get("data", {})
            outcome = data.get("outcome")

            if outcome not in ("success", "failure"):
                continue

            similarity = self._similarity(
                current_code,
                decision,
            )

            if similarity < self.similarity_threshold:
                continue

            normalized = self._normalized(
                data.get("scores", {})
            )

            for key in DecisionLearning.EVIDENCE_KEYS:
                value = abs(normalized[key])

                if value == 0.0:
                    continue

                weighted_value = (
                    value * similarity
                )

                statistics[key]["similarity"] += similarity

                if outcome == "success":
                    statistics[key]["success"] += weighted_value
                else:
                    statistics[key]["failure"] += weighted_value

        weights = {}

        for key, stats in statistics.items():
            success = stats["success"]
            failure = stats["failure"]

            total = success + failure

            if total == 0.0:
                weights[key] = 0.0
            else:
                weights[key] = (
                    (success - failure)
                    / total
                )

        return weights

    def score(self, current_code, decision_score):
        """
        Calcula a pontuação usando somente o conhecimento
        relevante para o contexto atual.
        """

        weights = self.learned_weights(
            current_code
        )

        normalized = self._normalized(
            decision_score.as_dict()
        )

        return sum(
            normalized[key] * weights.get(key, 0.0)
            for key in DecisionLearning.EVIDENCE_KEYS
        )

    def explain(self, current_code, decision_score):
        weights = self.learned_weights(
            current_code
        )

        normalized = self._normalized(
            decision_score.as_dict()
        )

        result = {}

        for key in DecisionLearning.EVIDENCE_KEYS:
            result[key] = {
                "normalized_value": normalized[key],
                "weight": weights.get(key, 0.0),
                "contribution": (
                    normalized[key]
                    * weights.get(key, 0.0)
                ),
            }

        return result
