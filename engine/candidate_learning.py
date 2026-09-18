from collections import defaultdict

from engine.structure import structural_profile, structural_similarity


class CandidateLearning:
    """
    Aprende quais candidatos foram úteis em determinados contextos.

    Diferente do aprendizado por evidência global, esta classe aprende
    diretamente a relação:

        contexto + candidato + região -> utilidade

    Um candidato intermediário pode não resolver o problema sozinho,
    mas ainda assim ser útil se aparecer no caminho que levou à solução.
    """

    def __init__(self, graph, similarity_threshold=0.5):
        self.graph = graph
        self.similarity_threshold = float(similarity_threshold)

    def _decisions(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node.get("type") == "decision"
        ]

    def _similarity(self, current_code, decision):
        previous_code = decision.get("data", {}).get("source_code", "")

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

    def _candidate_statistics(self, current_code):
        statistics = defaultdict(
            lambda: {
                "useful": 0.0,
                "not_useful": 0.0,
                "observations": 0.0,
            }
        )

        for decision in self._decisions():
            data = decision.get("data", {})
            candidate = data.get("candidate")

            if not candidate:
                continue

            # Ausência de crédito não significa fracasso.
            # Só evidências explícitas entram no aprendizado.
            if "useful" not in data:
                continue

            similarity = self._similarity(
                current_code,
                decision,
            )

            if similarity < self.similarity_threshold:
                continue

            key = (
                candidate,
                data.get("region_index"),
                data.get("region_type"),
            )

            statistics[key]["observations"] += similarity

            if data.get("useful") is True:
                statistics[key]["useful"] += similarity
            elif data.get("useful") is False:
                statistics[key]["not_useful"] += similarity

        return statistics

    def score_candidate(
        self,
        current_code,
        candidate,
    ):
        candidate_name = getattr(
            candidate,
            "name",
            None,
        )

        region_index = getattr(
            candidate,
            "region_index",
            None,
        )

        region_type = getattr(
            candidate,
            "region_type",
            None,
        )

        if not candidate_name:
            return 0.0

        statistics = self._candidate_statistics(
            current_code
        )

        key = (
            candidate_name,
            region_index,
            region_type,
        )

        stats = statistics.get(key)

        if not stats:
            return 0.0

        useful = stats["useful"]
        not_useful = stats["not_useful"]

        total = useful + not_useful

        if total == 0.0:
            return 0.0

        return (
            (useful - not_useful)
            / total
        )

    def rank(
        self,
        current_code,
        candidates,
    ):
        ranked = []

        for candidate in candidates:
            score = self.score_candidate(
                current_code,
                candidate,
            )

            ranked.append(
                {
                    "candidate": candidate,
                    "name": getattr(
                        candidate,
                        "name",
                        None,
                    ),
                    "region_index": getattr(
                        candidate,
                        "region_index",
                        None,
                    ),
                    "region_type": getattr(
                        candidate,
                        "region_type",
                        None,
                    ),
                    "candidate_learning_score": score,
                }
            )

        ranked.sort(
            key=lambda item: (
                item["candidate_learning_score"],
                item["name"] or "",
            ),
            reverse=True,
        )

        return ranked
