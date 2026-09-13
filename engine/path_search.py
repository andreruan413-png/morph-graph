from engine.memory import code_signature
from engine.trajectory_guidance import TrajectoryGuidance


class PathSearch:

    def __init__(
        self,
        graph,
        mutator,
        evaluator,
        max_depth=3,
        beam_width=3
    ):
        self.graph = graph
        self.mutator = mutator
        self.evaluator = evaluator
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.trajectory_guidance = TrajectoryGuidance(graph)

    def _score_node(self, node_id):

        best_score = 0.0

        for node in self.graph.nodes.values():

            if node["type"] != "evaluation":
                continue

            if (
                node["data"].get(
                    "target_node"
                )
                != node_id
            ):
                continue

            score = float(
                node["data"].get(
                    "score",
                    0.0
                )
            )

            if score > best_score:
                best_score = score

        return best_score

    def _next_id(self):

        index = 1

        while (
            f"path_code_{index:03d}"
            in self.graph.nodes
        ):
            index += 1

        return (
            f"path_code_{index:03d}"
        )

    def _create_candidate(
        self,
        source_id,
        candidate
    ):

        source = self.graph.nodes[
            source_id
        ]

        source_code = source[
            "data"
        ]["code"]

        new_code = candidate.code()

        return {
            "source_code": source_code,
            "new_code": new_code,
            "candidate": candidate
        }

    def _materialize_candidate(
        self,
        source_id,
        candidate,
        result
    ):

        new_code = result[
            "new_code"
        ]

        node_id = self._next_id()

        self.graph.add_node(
            node_id,
            "code",
            {
                "code": new_code,
                "language": "python",
                "generated_by": candidate.name,
                "mutation": candidate.name,
                "source_node": source_id,
                "mutation_type": "path_search"
            }
        )

        self.graph.connect(
            source_id,
            node_id,
            candidate.name
        )

        self.graph.history.append({
            "action": "path_transform",
            "source": source_id,
            "rule": candidate.name,
            "target": node_id
        })

        evaluation = self.evaluator(
            new_code
        )

        evaluation_id = (
            f"{node_id}_evaluation"
        )

        self.graph.add_node(
            evaluation_id,
            "evaluation",
            {
                "target_node": node_id,
                "success": bool(
                    evaluation["success"]
                ),
                "score": float(
                    evaluation["score"]
                ),
                "reason": evaluation.get(
                    "reason",
                    ""
                ),
                "passed": evaluation.get(
                    "passed",
                    0
                ),
                "total": evaluation.get(
                    "total",
                    0
                )
            }
        )

        self.graph.connect(
            node_id,
            evaluation_id,
            "evaluated_by"
        )

        return {
            "node_id": node_id,
            "rule": candidate.name,
            "score": float(
                evaluation["score"]
            ),
            "success": bool(
                evaluation["success"]
            )
        }

    def search(self, source_id):

        source = self.graph.nodes[
            source_id
        ]

        source_code = source[
            "data"
        ]["code"]

        # --------------------------------------------------
        # Estados já visitados.
        #
        # Usamos assinatura AST, não ID do nó.
        # Assim:
        #
        # A -> B -> A
        #
        # não pode acontecer.
        # --------------------------------------------------

        seen_signatures = {
            code_signature(
                source_code
            )
        }

        frontier = [
            {
                "node_id": source_id,
                "score": self._score_node(
                    source_id
                ),
                "path": []
            }
        ]

        best = {
            "node_id": source_id,
            "score": self._score_node(
                source_id
            ),
            "path": [],
            "depth": 0,
            "success": False
        }

        explored = 1

        # --------------------------------------------------
        # Busca por profundidade limitada.
        # --------------------------------------------------

        for depth in range(
            1,
            self.max_depth + 1
        ):

            next_frontier = []

            for state in frontier:

                current_id = state[
                    "node_id"
                ]

                current_node = (
                    self.graph.nodes[
                        current_id
                    ]
                )

                current_code = (
                    current_node[
                        "data"
                    ]["code"]
                )

                candidates = (
                    self.mutator.generate(
                        current_code
                    )
                )

                # Aprendizado de trajetória:
                # regras que historicamente foram o próximo passo
                # de caminhos bem-sucedidos recebem prioridade.
                learned_priorities = (
                    self.trajectory_guidance.priorities(
                        state["path"]
                    )
                )

                candidates = sorted(
                    candidates,
                    key=lambda candidate: (
                        learned_priorities.get(
                            candidate.name,
                            0
                        ),
                    ),
                    reverse=True
                )

                for candidate in candidates:

                    candidate_data = (
                        self._create_candidate(
                            current_id,
                            candidate
                        )
                    )

                    new_code = (
                        candidate_data[
                            "new_code"
                        ]
                    )

                    signature = (
                        code_signature(
                            new_code
                        )
                    )

                    # --------------------------------------------------
                    # Não visitar novamente o mesmo estado estrutural.
                    # --------------------------------------------------

                    if signature in seen_signatures:
                        continue

                    seen_signatures.add(
                        signature
                    )

                    result = (
                        self._materialize_candidate(
                            current_id,
                            candidate,
                            candidate_data
                        )
                    )

                    explored += 1

                    path = (
                        state["path"]
                        + [candidate.name]
                    )

                    result["depth"] = depth
                    result["path"] = path

                    next_frontier.append(
                        result
                    )

                    # --------------------------------------------------
                    # Atualiza melhor estado.
                    # --------------------------------------------------

                    if (
                        result["score"]
                        > best["score"]
                    ):
                        best = result

                    # --------------------------------------------------
                    # Solução completa.
                    # --------------------------------------------------

                    if result["success"]:

                        return {
                            "success": True,
                            "best": result,
                            "path": path,
                            "explored": explored
                        }

            if not next_frontier:
                break

            # --------------------------------------------------
            # Mantém os melhores estados.
            #
            # IMPORTANTE:
            # não exigimos que o próximo estado tenha score
            # maior que o pai. Isso permite atravessar estados
            # intermediários.
            # --------------------------------------------------

            next_frontier.sort(
                key=lambda item: (
                    item["score"],
                    -len(
                        item["path"]
                    )
                ),
                reverse=True
            )

            frontier = (
                next_frontier[
                    :self.beam_width
                ]
            )

        return {
            "success": False,
            "best": best,
            "path": best.get(
                "path",
                []
            ),
            "explored": explored
        }
