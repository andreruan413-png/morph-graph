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

    def evolve_with_exploration(
        self,
        source_id,
        generations=5,
        allow_non_improving=True,
        max_states=50,
    ):
        """
        Busca evolutiva que permite atravessar estados
        temporariamente não melhores.

        Mantém o ranking e a memória existentes, mas amplia
        a fronteira de busca em vez de exigir melhoria imediata.
        """

        source = self.graph.nodes.get(source_id)

        if not source:
            raise ValueError(
                f"Nó de origem não existe: {source_id}"
            )

        self.memory.remember(source_id)

        source_code = source["data"].get("code", "")

        if self.tests is not None:
            initial_result = evaluate_problem(
                source_code,
                self.tests,
            )
            initial_score = initial_result.score
        else:
            from engine.verifier import verify_python_code

            initial_result = verify_python_code(
                source_code
            )

            initial_score = (
                1.0
                if initial_result.success
                else 0.0
            )

        frontier = [
            {
                "node_id": source_id,
                "score": initial_score,
                "path": [],
            }
        ]

        visited_codes = {
            source_code
        }

        generations_data = []

        best_state = frontier[0]

        states_explored = 0

        for generation in range(
            1,
            generations + 1
        ):

            next_frontier = []

            for state in frontier:

                if states_explored >= max_states:
                    break

                current_node_id = state["node_id"]

                candidates = self.generate_candidates(
                    current_node_id
                )

                ranked = rank_candidates(
                    self.graph,
                    current_node_id,
                    candidates,
                )

                # O ranking existente pode retornar dicionários
                # com formatos diferentes. Recuperamos o candidato
                # sem assumir uma chave "name".
                ordered_candidates = []

                for item in ranked:

                    if hasattr(item, "code"):
                        ordered_candidates.append(item)
                        continue

                    if isinstance(item, dict):

                        candidate = item.get(
                            "candidate"
                        )

                        if candidate is not None:
                            ordered_candidates.append(
                                candidate
                            )
                            continue

                        candidate_name = (
                            item.get("name")
                            or item.get("rule")
                            or item.get("candidate_name")
                        )

                        if candidate_name:
                            candidate = next(
                                (
                                    candidate
                                    for candidate in candidates
                                    if candidate.name
                                    == candidate_name
                                ),
                                None,
                            )

                            if candidate is not None:
                                ordered_candidates.append(
                                    candidate
                                )

                # Fallback: nenhum formato conhecido foi encontrado.
                # Não inventamos candidato; usamos a lista original.
                if not ordered_candidates:
                    ordered_candidates = list(candidates)

                selected = None

                for candidate in ordered_candidates:

                    if states_explored >= max_states:
                        break

                    candidate_code = candidate.code()

                    if candidate_code in visited_codes:
                        continue

                    visited_codes.add(candidate_code)

                    result = self.evaluate_candidate(
                        current_node_id,
                        candidate,
                    )

                    states_explored += 1

                    candidate_state = {
                        "node_id": result["node_id"],
                        "score": result["score"],
                        "path": state["path"] + [
                            candidate.name
                        ],
                    }

                    if (
                        result["node_id"] is not None
                        and result["score"]
                        > best_state["score"]
                    ):
                        best_state = candidate_state

                    if selected is None:
                        selected = {
                            "node_id": result["node_id"],
                            "rule": candidate.name,
                            "score": result["score"],
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
                        }

                    if result["node_id"] is None:
                        continue

                    if (
                        result["score"] >= state["score"]
                        or allow_non_improving
                    ):
                        next_frontier.append(
                            candidate_state
                        )

                    if result["score"] >= 1.0:

                        generations_data.append(
                            {
                                "generation": generation,
                                "source": current_node_id,
                                "selected": selected,
                                "states_explored": states_explored,
                            }
                        )

                        return {
                            "success": True,
                            "final_node": result["node_id"],
                            "final_score": result["score"],
                            "generations": generations_data,
                            "states_explored": states_explored,
                            "path": candidate_state["path"],
                        }

            generations_data.append(
                {
                    "generation": generation,
                    "source": (
                        frontier[0]["node_id"]
                        if frontier
                        else source_id
                    ),
                    "selected": selected or {},
                    "states_explored": states_explored,
                }
            )

            if not next_frontier:
                break

            next_frontier.sort(
                key=lambda item: (
                    item["score"],
                    -len(item["path"]),
                ),
                reverse=True,
            )

            frontier = next_frontier[
                :max_states
            ]

        return {
            "success": best_state["score"] >= 1.0,
            "final_node": best_state["node_id"],
            "final_score": best_state["score"],
            "generations": generations_data,
            "states_explored": states_explored,
            "path": best_state["path"],
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
