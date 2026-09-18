from engine.decision import DecisionScore


class DecisionRecorder:
    """
    Transforma uma decisão do PathSearch em um nó persistente
    do Graph e mantém a ligação com o candidato exato.
    """

    def __init__(self, graph):
        self.graph = graph

    def find_problem_id(self, source_id):
        """
        Tenta descobrir o problema associado ao nó de origem.
        """

        if not source_id:
            return None

        # Caso direto: problema -> candidato
        for edge in self.graph.edges:
            if (
                edge.get("target") == source_id
                and edge.get("relation") == "has_candidate"
            ):
                return edge.get("source")

        # Caso de um candidato gerado posteriormente:
        # sobe pela cadeia source_node.
        current_id = source_id
        visited = set()

        while current_id and current_id not in visited:
            visited.add(current_id)

            node = self.graph.nodes.get(current_id)

            if not node:
                break

            data = node.get("data", {})

            source_node = data.get("source_node")

            if source_node:
                current_id = source_node
                continue

            break

        for edge in self.graph.edges:
            if (
                edge.get("target") == current_id
                and edge.get("relation") == "has_candidate"
            ):
                return edge.get("source")

        return None

    def record(
        self,
        problem_id,
        candidate,
        decision_score,
        path=None,
        selected=False,
        candidate_node_id=None,
        outcome=None,
        source_code=None,
    ):
        if not isinstance(decision_score, DecisionScore):
            raise TypeError(
                "decision_score deve ser uma instância de DecisionScore"
            )

        path = list(path or [])

        decision_id = f"decision_{len(self.graph.nodes):04d}"

        candidate_name = getattr(candidate, "name", None)
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
        mutation_type = getattr(
            candidate,
            "mutation_type",
            None,
        )

        data = {
            "problem_id": problem_id,
            "candidate": candidate_name,
            "region_index": region_index,
            "region_type": region_type,
            "mutation_type": mutation_type,
            "path": path,
            "selected": bool(selected),
            "scores": decision_score.as_dict(),
            "source_code": source_code or "",
        }

        if outcome in ("success", "failure"):
            data["outcome"] = outcome

        if candidate_node_id:
            data["candidate_node_id"] = candidate_node_id

        node = self.graph.add_node(
            decision_id,
            "decision",
            data,
        )

        if (
            problem_id
            and problem_id in self.graph.nodes
        ):
            self.graph.connect(
                problem_id,
                decision_id,
                "produced_decision",
            )

        # Preferência absoluta: usar o ID exato.
        if (
            candidate_node_id
            and candidate_node_id in self.graph.nodes
        ):
            self.graph.connect(
                decision_id,
                candidate_node_id,
                "decision_for",
            )

        return node
