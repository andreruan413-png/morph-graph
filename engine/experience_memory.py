from engine.structure import (
    structural_profile,
    structural_similarity
)


class ExperienceMemory:

    def __init__(self, graph):
        self.graph = graph

    def experiences(self):

        return [
            node
            for node in self.graph.nodes.values()
            if node["type"] == "experience"
        ]

    def find_similar_experiences(
        self,
        code,
        minimum_similarity=0.70
    ):

        target_profile = structural_profile(code)

        matches = []

        for experience in self.experiences():

            data = experience["data"]

            solution_id = data.get(
                "solution_node"
            )

            solution = self.graph.nodes.get(
                solution_id
            )

            if not solution:
                continue

            generations = data.get(
                "generations",
                []
            )

            if not generations:
                continue

            source_id = generations[-1].get(
                "source"
            )

            if not source_id:
                continue

            source = self.graph.nodes.get(
                source_id
            )

            if not source:
                continue

            source_code = source["data"].get(
                "code"
            )

            if not source_code:
                continue

            try:

                source_profile = structural_profile(
                    source_code
                )

            except SyntaxError:

                continue

            similarity = structural_similarity(
                target_profile,
                source_profile
            )

            if similarity < minimum_similarity:
                continue

            matches.append({
                "experience_id": experience["id"],
                "problem_id": data.get(
                    "problem_id"
                ),
                "solution_node": solution_id,
                "source_node": source_id,
                "score": float(
                    data.get("score", 0.0)
                ),
                "similarity": similarity,
                "generations": generations
            })

        matches.sort(
            key=lambda item: (
                item["similarity"],
                item["score"]
            ),
            reverse=True
        )

        return matches

    def mutation_history(
        self,
        code,
        minimum_similarity=0.70
    ):

        experiences = self.find_similar_experiences(
            code,
            minimum_similarity
        )

        mutations = []

        for experience in experiences:

            for generation in experience[
                "generations"
            ]:

                selected = generation.get(
                    "selected",
                    {}
                )

                rule = selected.get(
                    "rule"
                )

                if not rule:
                    continue

                mutations.append({
                    "rule": rule,
                    "experience_id": (
                        experience["experience_id"]
                    ),
                    "similarity": (
                        experience["similarity"]
                    ),
                    "score": float(
                        selected.get(
                            "score",
                            0.0
                        )
                    )
                })

        mutations.sort(
            key=lambda item: (
                item["similarity"],
                item["score"]
            ),
            reverse=True
        )

        return mutations

    def mutation_priority(
        self,
        code
    ):

        priorities = {}

        history = self.mutation_history(
            code
        )

        for item in history:

            rule = item["rule"]

            evidence = (
                item["similarity"]
                * item["score"]
            )

            previous = priorities.get(
                rule,
                0.0
            )

            priorities[rule] = max(
                previous,
                evidence
            )

        return priorities
