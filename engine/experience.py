class ExperienceRecorder:

    def __init__(self, graph):
        self.graph = graph

    def record_solution(
        self,
        problem_id,
        result
    ):
        final_node = result.get("final_node")
        final_score = result.get("final_score")

        if not final_node:
            return None

        experience_id = (
            f"experience_{len(self.graph.nodes):03d}"
        )

        generations = result.get(
            "generations",
            []
        )

        experience = self.graph.add_node(
            experience_id,
            "experience",
            {
                "problem_id": problem_id,
                "solution_node": final_node,
                "score": final_score,
                "generations": generations
            }
        )

        self.graph.connect(
            problem_id,
            experience_id,
            "produced_experience"
        )

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

            rule = selected.get(
                "rule"
            )

            source = generation.get(
                "source"
            )

            target = selected.get(
                "node_id"
            )

            if source and target:

                self.graph.connect(
                    experience_id,
                    source,
                    "trajectory_source"
                )

                self.graph.connect(
                    experience_id,
                    target,
                    "trajectory_result"
                )

        return experience_id
