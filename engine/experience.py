class ExperienceRecorder:
    def __init__(self, graph):
        self.graph = graph

    def _extract_trajectory(self, generations):
        trajectory = []

        for generation in generations:
            selected = generation.get("selected", {})

            rule = selected.get("rule")

            if not rule:
                continue

            trajectory.append({
                "rule": rule,
                "region_index": selected.get("region_index"),
                "region_type": selected.get("region_type"),
            })

        return trajectory

    def _source_code(self, problem_id):
        for edge in self.graph.edges:
            if (
                edge.get("source") == problem_id
                and edge.get("relation") == "has_candidate"
            ):
                node = self.graph.nodes.get(edge.get("target"))

                if node and node.get("type") == "code":
                    return node.get("data", {}).get("code", "")

        return ""

    def record_solution(
        self,
        problem_id,
        result
    ):
        # Compatibilidade com EvolutionEngine
        # e com PathSearch.

        final_node = result.get("final_node")

        # PathSearch usa "node_id" e "score".
        if not final_node:
            final_node = result.get("node_id")

        final_score = result.get("final_score")

        if final_score is None:
            final_score = result.get("score", 0.0)

        if not final_node:
            return None

        experience_id = (
            f"experience_{len(self.graph.nodes):03d}"
        )

        # EvolutionEngine fornece generations.
        generations = result.get(
            "generations",
            []
        )

        # PathSearch fornece path.
        path = result.get("path", [])

        if not generations and path:
            generations = []

            current_node = result.get(
                "source_id"
            )

            for index, rule in enumerate(path):
                generations.append({
                    "source": current_node,
                    "selected": {
                        "rule": rule,
                        "node_id": None,
                        "region_index": None,
                        "region_type": None,
                    }
                })

        trajectory = self._extract_trajectory(
            generations
        )

        # Se PathSearch não trouxe regiões nas
        # generations, recuperamos as informações
        # diretamente dos nós do grafo.
        for step in trajectory:
            if step.get("region_index") is not None:
                continue

            rule = step.get("rule")

            for node in self.graph.nodes.values():
                data = node.get("data", {})

                if data.get("generated_by") == rule:
                    step["region_index"] = data.get(
                        "region_index"
                    )
                    step["region_type"] = data.get(
                        "region_type"
                    )
                    break

        source_code = self._source_code(
            problem_id
        )

        experience = self.graph.add_node(
            experience_id,
            "experience",
            {
                "problem_id": problem_id,
                "solution_node": final_node,
                "source_code": source_code,
                "score": final_score,
                "generations": generations,
                "trajectory": trajectory,
            }
        )

        self.graph.connect(
            problem_id,
            experience_id,
            "produced_experience"
        )

        if final_node in self.graph.nodes:
            self.graph.connect(
                experience_id,
                final_node,
                "learned_solution"
            )

        for generation in generations:

            selected = generation.get(
                "selected",
                {}
            )

            source = generation.get(
                "source"
            )

            target = selected.get(
                "node_id"
            )

            if source and source in self.graph.nodes:
                self.graph.connect(
                    experience_id,
                    source,
                    "trajectory_source"
                )

            if target and target in self.graph.nodes:
                self.graph.connect(
                    experience_id,
                    target,
                    "trajectory_result"
                )

        return experience_id

