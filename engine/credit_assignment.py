class TrajectoryCredit:
    """
    Atribui crédito aos candidatos que fizeram parte
    da trajetória que levou à solução.

    Um candidato intermediário não precisa resolver o problema
    sozinho para ser considerado útil.
    """

    def __init__(self, graph):
        self.graph = graph

    def assign(self, decision_node_ids):
        credited = []

        for decision_id in decision_node_ids:
            decision = self.graph.nodes.get(decision_id)

            if not decision:
                continue

            data = decision.setdefault("data", {})
            scores = data.get("scores", {})

            try:
                fitness_delta = float(
                    scores.get("fitness_delta", 0.0)
                )
            except (TypeError, ValueError):
                fitness_delta = 0.0

            data["fitness_delta"] = fitness_delta

            # Crédito de trajetória significa que a decisão
            # pertenceu ao caminho que efetivamente chegou
            # à solução.
            data["trajectory_credit"] = 1.0

            # Utilidade semântica é separada do crédito de
            # trajetória: só existe quando houve melhoria.
            data["semantic_credit"] = max(
                0.0,
                fitness_delta,
            )

            data["useful"] = fitness_delta > 0.0

            credited.append(decision_id)

        return credited

    def penalize_uncredited(self, decision_node_ids):
        penalized = []

        for decision_id in decision_node_ids:
            decision = self.graph.nodes.get(decision_id)

            if not decision:
                continue

            data = decision.setdefault("data", {})

            if data.get("useful"):
                continue

            data["useful"] = False
            data["trajectory_credit"] = -1.0

            penalized.append(decision_id)

        return penalized
