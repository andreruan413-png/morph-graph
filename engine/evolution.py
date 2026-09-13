from engine.evaluator import Evaluation, record_evaluation
from engine.memory import GraphMemory
from engine.auto_mutation import AutomaticASTMutator
from engine.strategy import rank_candidates
from engine.problem_evaluator import evaluate_problem


class EvolutionEngine:

    def __init__(self, graph, tests=None):

        self.graph = graph
        self.tests = tests

        self.memory = GraphMemory(
            graph
        )

        self.mutator = AutomaticASTMutator()

    def _next_code_id(self):

        index = 1

        while f"code_{index:03d}" in self.graph.nodes:
            index += 1

        return f"code_{index:03d}"

    def generate_candidates(
        self,
        source_id
    ):

        source = self.graph.nodes[
            source_id
        ]

        if source["type"] != "code":
            raise ValueError(
                "O nó de origem precisa ser do tipo 'code'."
            )

        return self.mutator.generate(
            source["data"]["code"]
        )

    def evaluate_candidate(
        self,
        source_id,
        candidate
    ):

        code = candidate.code()

        if self.memory.has_seen(code):

            return {
                "node_id": None,
                "rule": candidate.name,
                "success": False,
                "score": 0.0,
                "reason": "estrutura já explorada pelo grafo",
                "duplicate": True,
                "passed": 0,
                "total": 0
            }

        new_id = self._next_code_id()

        self.graph.add_node(
            new_id,
            "code",
            {
                "code": code,
                "language": "python",
                "generated_by": candidate.name,
                "mutation": candidate.name,
                "source_node": source_id,
                "mutation_type": "automatic_AST"
            }
        )

        self.graph.connect(
            source_id,
            new_id,
            candidate.name
        )

        self.graph.history.append({
            "action": "automatic_transform",
            "source": source_id,
            "rule": candidate.name,
            "target": new_id
        })

        if self.tests is not None:

            verification = evaluate_problem(
                code,
                self.tests
            )

        else:

            from engine.verifier import verify_python_code

            verification = verify_python_code(
                code
            )

        evaluation = Evaluation(
            verification.success,
            verification.score,
            verification.reason
        )

        evaluation_id = record_evaluation(
            self.graph,
            new_id,
            evaluation
        )

        self.memory.remember(
            new_id
        )

        return {
            "node_id": new_id,
            "evaluation_id": evaluation_id,
            "rule": candidate.name,
            "success": verification.success,
            "score": verification.score,
            "reason": verification.reason,
            "duplicate": False,
            "passed": getattr(
                verification,
                "passed",
                0
            ),
            "total": getattr(
                verification,
                "total",
                0
            )
        }

    def evolve(
        self,
        source_id,
        generations=5
    ):

        current_id = source_id

        current_score = 0.0

        history = []

        self.memory.remember(
            source_id
        )

        for generation in range(
            1,
            generations + 1
        ):

            print(
                f"\n=== GERAÇÃO {generation} ==="
            )

            candidates = self.generate_candidates(
                current_id
            )

            print(
                f"Mutações descobertas: "
                f"{len(candidates)}"
            )

            ranked = rank_candidates(
                self.graph,
                current_id,
                candidates
            )

            results = []

            for position, item in enumerate(
                ranked,
                start=1
            ):

                candidate = item["candidate"]

                result = self.evaluate_candidate(
                    current_id,
                    candidate
                )

                result["strategy_position"] = position

                result["historical_success_rate"] = (
                    item["success_rate"]
                )

                result["historical_average_score"] = (
                    item["average_score"]
                )

                result["structural_similarity"] = (
                    item["similarity"]
                )

                results.append(
                    result
                )

                print(
                    f"{candidate.name} -> "
                    f"score={result['score']} "
                    f"success={result['success']} "
                    f"duplicate={result['duplicate']} "
                    f"hist_rate="
                    f"{item['success_rate']:.2f}"
                )

            valid = [
                result
                for result in results
                if (
                    not result["duplicate"]
                    and result["score"] > current_score
                )
            ]

            if not valid:

                print(
                    "Nenhum candidato apresentou melhoria."
                )

                break

            best = max(
                valid,
                key=lambda item: (
                    item["score"],
                    item["historical_success_rate"],
                    item["historical_average_score"],
                    item["structural_similarity"]
                )
            )

            history.append({
                "generation": generation,
                "source": current_id,
                "previous_score": current_score,
                "selected": best
            })

            print(
                f"SELECIONADO: "
                f"{best['node_id']} "
                f"({best['rule']}) "
                f"score={best['score']}"
            )

            current_id = best[
                "node_id"
            ]

            current_score = best[
                "score"
            ]

            if current_score >= 1.0:

                print(
                    "SOLUÇÃO ENCONTRADA. "
                    "Fitness máximo atingido."
                )

                break

        return {
            "final_node": current_id,
            "final_score": current_score,
            "generations": history
        }
