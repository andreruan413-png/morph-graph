from engine.path_search import PathSearch
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
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

    def _find_connected_node(self, relation, node_type):
        for edge in self.graph.edges:
            if (
                edge["source"] == self.problem_id
                and edge["relation"] == relation
            ):
                target_id = edge["target"]
                target = self.graph.nodes.get(target_id)

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

    def solve(self, generations=10, beam_width=3, max_depth=None):
        tests = self._find_tests()
        candidate_id = self._find_candidate()
        if max_depth is None:
            max_depth = generations

        def evaluator(code):
            return evaluate_problem(
                code,
                tests
            ).as_dict()

        search = PathSearch(
            graph=self.graph,
            mutator=AutomaticASTMutator(),
            evaluator=evaluator,
            problem_id=self.problem_id,
            max_depth=max_depth,
            beam_width=beam_width,
            use_trajectory=True,
            use_structure=True,
            use_graph_guidance=True,
            use_context_guidance=True,
            use_failure_guidance=True,
            use_decision_score=True,
        )

        result = search.search(candidate_id)

        # Compatibilidade com a API antiga do ProblemEngine.
        result["final_node"] = result.get("node_id")
        result["final_score"] = result.get("score", 0.0)

        if "generations" not in result:
            result["generations"] = []

            path = result.get("path", [])
            region_path = result.get("region_path", [])

            for index, rule in enumerate(path):
                region = (
                    region_path[index]
                    if index < len(region_path)
                    else {}
                )

                result["generations"].append({
                    "generation": index + 1,
                    "source": (
                        candidate_id
                        if index == 0
                        else None
                    ),
                    "selected": {
                        "rule": rule,
                        "node_id": None,
                        "score": result.get("score", 0.0),
                        "region_index": region.get(
                            "region_index"
                        ),
                        "region_type": region.get(
                            "region_type"
                        ),
                    },
                })

        final_node = result.get("node_id")
        final_score = result.get("score", 0.0)

        if final_node:
            if final_node != candidate_id:
                self.graph.connect(
                    self.problem_id,
                    final_node,
                    "generated_candidate"
                )

            if result.get("success"):
                self.graph.connect(
                    self.problem_id,
                    final_node,
                    "solved_by"
                )

        recorder = ExperienceRecorder(self.graph)

        experience_id = recorder.record_solution(
            self.problem_id,
            result
        )

        result["experience_node"] = experience_id

        return result
