from engine.evolution import EvolutionEngine
from engine.experience import ExperienceRecorder


class ProblemEngine:

    def __init__(self, graph, problem_id):

        self.graph = graph
        self.problem_id = problem_id

        if problem_id not in graph.nodes:
            raise ValueError(
                f"Problema não encontrado: {problem_id}"
            )

        problem = graph.nodes[problem_id]

        if problem["type"] != "problem":
            raise ValueError(
                f"O nó '{problem_id}' não é um problema."
            )

    def _find_connected_node(
        self,
        relation,
        node_type
    ):

        for edge in self.graph.edges:

            if (
                edge["source"] == self.problem_id
                and edge["relation"] == relation
            ):

                target_id = edge["target"]

                target = self.graph.nodes.get(
                    target_id
                )

                if (
                    target
                    and target["type"] == node_type
                ):
                    return target_id

        return None

    def _find_tests(self):

        tests_id = self._find_connected_node(
            "has_tests",
            "tests"
        )

        if not tests_id:
            raise ValueError(
                "O problema não possui nó de testes."
            )

        return self.graph.nodes[
            tests_id
        ]["data"]["content"]

    def _find_candidate(self):

        candidate_id = self._find_connected_node(
            "has_candidate",
            "code"
        )

        if not candidate_id:
            raise ValueError(
                "O problema não possui candidato inicial."
            )

        return candidate_id

    def solve(self, generations=10):

        tests = self._find_tests()

        candidate_id = self._find_candidate()

        engine = EvolutionEngine(
            self.graph,
            tests=tests
        )

        result = engine.evolve(
            candidate_id,
            generations=generations
        )

        final_node = result[
            "final_node"
        ]

        final_score = result[
            "final_score"
        ]

        if final_node != candidate_id:

            self.graph.connect(
                self.problem_id,
                final_node,
                "generated_candidate"
            )

        if final_score >= 1.0:

            self.graph.connect(
                self.problem_id,
                final_node,
                "solved_by"
            )

        recorder = ExperienceRecorder(
            self.graph
        )

        experience_id = (
            recorder.record_solution(
                self.problem_id,
                result
            )
        )

        result["experience_node"] = (
            experience_id
        )

        return result
