from engine.trajectory_guidance import TrajectoryGuidance
from engine.graph_guidance import GraphGuidance
from engine.context_guidance import ContextGuidance
from engine.failure_guidance import FailureGuidance
from engine.evaluator import Evaluation, record_evaluation
from engine.decision import DecisionScore
from engine.decision_recorder import DecisionRecorder
from engine.context_decision_learning import ContextDecisionLearning
from engine.candidate_learning import CandidateLearning
from engine.sequence_learning import SequenceLearning


class PathSearch:
    def __init__(
        self,
        graph,
        mutator,
        evaluator,
        problem_id=None,
        max_depth=3,
        beam_width=3,
        use_trajectory=True,
        use_structure=True,
        use_pruner=False,
        transition_memory=None,
        context_memory=None,
        context_tests=None,
        use_graph_guidance=False,
        use_context_guidance=False,
        use_failure_guidance=False,
        use_decision_score=False,
    ):
        self.graph = graph
        self.mutator = mutator
        self.evaluator = evaluator
        self.problem_id = problem_id
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.use_trajectory = use_trajectory
        self.use_structure = use_structure
        self.use_pruner = use_pruner
        self.transition_memory = transition_memory
        self.context_memory = context_memory
        self.context_tests = context_tests
        self.use_graph_guidance = use_graph_guidance
        self.use_context_guidance = use_context_guidance

        self.use_failure_guidance = use_failure_guidance
        self.use_decision_score = use_decision_score
        self.decision_history = []
        self.decision_recorder = DecisionRecorder(graph)
        self.search_decision_ids = []
        self.context_decision_learning = ContextDecisionLearning(graph)
        self.candidate_learning = CandidateLearning(graph)
        self.sequence_learning = SequenceLearning(graph)

        self.trajectory_guidance = (
            TrajectoryGuidance(
                graph,
                problem_id=self.problem_id,
            )
        )
        self.graph_guidance = (
            GraphGuidance(
                graph,
                problem_id=self.problem_id,
            )
            if self.use_graph_guidance
            else None
        )

        self.context_guidance = (
            ContextGuidance(graph)
            if self.use_context_guidance
            else None
        )

        self.failure_guidance = (
            FailureGuidance(graph)
            if self.use_failure_guidance
            else None
        )

        if self.transition_memory is None:
            from engine.transition_memory import TransitionMemory

            self.transition_memory = TransitionMemory(graph)

        if self.use_pruner:
            from engine.region_pruner import RegionPruner

            self.region_pruner = RegionPruner(graph)
        else:
            self.region_pruner = None

    def _context_next_steps(self, path):
        if (
            self.context_memory is None
            or self.context_tests is None
        ):
            return {}

        try:
            trajectories = (
                self.context_memory.trajectories_for(
                    self.context_tests
                )
            )
        except Exception:
            return {}

        suggestions = {}
        prefix = list(path)

        for trajectory in trajectories:
            learned_path = trajectory.get(
                "path",
                []
            )

            score = float(
                trajectory.get(
                    "score",
                    0.0
                )
            )

            if len(learned_path) <= len(prefix):
                continue

            if learned_path[:len(prefix)] != prefix:
                continue

            next_rule = learned_path[len(prefix)]

            suggestions[next_rule] = (
                suggestions.get(
                    next_rule,
                    0.0
                ) + score
            )

        return suggestions

    def _context_region_priority(
        self,
        path,
        candidate,
    ):
        if (
            self.context_memory is None
            or self.context_tests is None
        ):
            return 0.0

        try:
            trajectories = (
                self.context_memory.trajectories_for(
                    self.context_tests
                )
            )
        except Exception:
            return 0.0

        prefix = list(path)
        priority = 0.0

        candidate_rule = getattr(
            candidate,
            "name",
            None
        )

        candidate_region_index = getattr(
            candidate,
            "region_index",
            None
        )

        candidate_region_type = getattr(
            candidate,
            "region_type",
            None
        )

        for trajectory in trajectories:

            learned_path = trajectory.get(
                "path",
                []
            )

            learned_regions = trajectory.get(
                "region_path",
                []
            )

            score = float(
                trajectory.get(
                    "score",
                    0.0
                )
            )

            if len(learned_path) <= len(prefix):
                continue

            if learned_path[:len(prefix)] != prefix:
                continue

            expected_rule = learned_path[len(prefix)]

            if expected_rule != candidate_rule:
                continue

            if len(learned_regions) <= len(prefix):
                priority += score
                continue

            expected_region = learned_regions[len(prefix)]

            expected_region_index = expected_region.get(
                "region_index"
            )

            expected_region_type = expected_region.get(
                "region_type"
            )

            if (
                expected_region_index
                == candidate_region_index
                and expected_region_type
                == candidate_region_type
            ):
                priority += 10.0 * score
            else:
                priority += score

        return priority

    def _trajectory_region_priority(
        self,
        path,
        candidate,
    ):
        if not self.use_trajectory:
            return 0.0

        try:
            memory = self.trajectory_guidance.memory
            regions = memory.next_regions(path)
        except Exception:
            return 0.0

        priority = 0.0

        for key, count in regions.items():
            rule, region_index, region_type = key

            if rule != candidate.name:
                continue

            if (
                region_index == candidate.region_index
                and region_type == candidate.region_type
            ):
                priority += float(count)

        return priority

    def _record_trajectory_credit(self, successful_path):
        """
        Atribui crédito positivo às decisões que pertencem
        à trajetória que efetivamente levou à solução.

        O crédito é atribuído pela posição exata da etapa
        na trajetória, evitando ambiguidades quando o mesmo
        candidato aparece mais de uma vez.
        """
        if not successful_path:
            return []

        from engine.credit_assignment import TrajectoryCredit

        credit = TrajectoryCredit(self.graph)

        useful_ids = []

        for decision_id in self.search_decision_ids:
            decision = self.graph.nodes.get(decision_id)

            if not decision:
                continue

            data = decision.get("data", {})
            candidate_name = data.get("candidate")
            decision_path = data.get("path", [])

            for candidate_index, expected_candidate in enumerate(
                successful_path
            ):
                if candidate_name != expected_candidate:
                    continue

                expected_path = successful_path[
                    :candidate_index
                ]

                if decision_path == expected_path:
                    useful_ids.append(decision_id)
                    break

        return credit.assign(useful_ids)

    def _decision_score_for_candidate(self, path, candidate):
        candidate_learning_score = (
            self.candidate_learning.score_candidate(
                self._current_code,
                candidate,
            )
        )
        sequence_learning_score = self.sequence_learning.score(
            path,
            candidate.name,
        )

        # Aprendizado estrutural da sequência:
        # ignora o nome textual da mutação e usa
        # (região, tipo de região, tipo de mutação).
        path_signatures = []

        for previous_name in path:
            signature = None

            for node in self.graph.nodes.values():
                data = node.get("data", {})

                if data.get("candidate") != previous_name:
                    continue

                if data.get("path", []) != path[:len(path_signatures)]:
                    continue

                signature = (
                    data.get("region_index"),
                    data.get("region_type"),
                    data.get("mutation_type"),
                )
                break

            if signature is None:
                break

            path_signatures.append(signature)

        candidate_signature = (
            getattr(candidate, "region_index", None),
            getattr(candidate, "region_type", None),
            getattr(candidate, "mutation_type", None),
        )

        structural_sequence_score = (
            self.sequence_learning.score_structural(
                path_signatures,
                candidate_signature,
            )
        )

        context_next = self._context_next_steps(path)

        transition_priority = (
            self.transition_memory.mutation_priority(
                self._current_code
            )
        )
        prefix_priority = {}
        if hasattr(self.transition_memory, "next_steps"):
            prefix_priority = self.transition_memory.next_steps(
                self._current_code,
                path,
            )
        for name, value in prefix_priority.items():
            transition_priority[name] = (
                transition_priority.get(name, 0.0)
                + float(value)
            )

        learned_priority = {}
        if self.use_trajectory:
            learned_priority = (
                self.trajectory_guidance.priorities(path)
            )

        graph_score = (
            self.graph_guidance.score_candidate(
                candidate,
                path
            )
            if self.graph_guidance is not None
            else 0.0
        )

        context_guidance_score = (
            self.context_guidance.candidate_score(
                self._current_code,
                candidate,
                path,
            )
            if self.context_guidance is not None
            else 0.0
        )

        failure_guidance_score = (
            self.failure_guidance.score_candidate(
                candidate,
                current_code=self._current_code,
            )
            if self.failure_guidance is not None
            else 0.0
        )

        transition_score = transition_priority.get(
            candidate.name,
            0.0,
        )

        learned_score = learned_priority.get(
            candidate.name,
            0.0,
        )

        trajectory_region_priority = (
            self._trajectory_region_priority(
                path,
                candidate,
            )
        )

        contextual_learning_score = (
            self.context_decision_learning.score(
                self._current_code,
                DecisionScore.from_values(
                    context=context_guidance_score,
                    trajectory=trajectory_region_priority,
                    graph=graph_score,
                    failure=failure_guidance_score,
                    transition=transition_score,
                    learned=learned_score,
                ),
            )
        )

        learned_score += contextual_learning_score

        # Aprendizado específico do candidato:
        # decisões que receberam crédito positivo na trajetória
        # vencedora passam a influenciar diretamente o ranking.
        # O aprendizado específico do candidato permanece
        # separado do aprendizado global para não ser esmagado
        # pelas penalizações das outras evidências.
        decision_score = DecisionScore.from_values(
            context=context_guidance_score,
            trajectory=trajectory_region_priority,
            graph=graph_score,
            failure=failure_guidance_score,
            transition=transition_score,
            learned=learned_score,
            candidate_learning=candidate_learning_score,
            sequence_learning=sequence_learning_score,
            structural_sequence=structural_sequence_score,
        )

        return decision_score

    def _candidate_sort_key(
        self,
        path,
        candidate,
    ):
        context_next = self._context_next_steps(path)

        context_rule_priority = context_next.get(
            candidate.name,
            0.0,
        )

        context_region_priority = (
            self._context_region_priority(
                path,
                candidate,
            )
        )

        trajectory_region_priority = (
            self._trajectory_region_priority(
                path,
                candidate,
            )
        )

        transition_priority = (
            self.transition_memory.mutation_priority(
                self._current_code
            )
        )
        prefix_priority = {}
        if hasattr(self.transition_memory, "next_steps"):
            prefix_priority = self.transition_memory.next_steps(
                self._current_code,
                path,
            )
        for name, value in prefix_priority.items():
            transition_priority[name] = (
                transition_priority.get(name, 0.0)
                + float(value)
            )

        transition_score = transition_priority.get(
            candidate.name,
            0.0,
        )

        learned_priority = {}
        if self.use_trajectory:
            learned_priority = (
                self.trajectory_guidance.priorities(path)
            )

        learned_score = learned_priority.get(
            candidate.name,
            0.0,
        )

        decision_score = self._decision_score_for_candidate(
            path,
            candidate,
        )

        if self.use_decision_score:
            decision_record = {
                "candidate": candidate.name,
                "region_index": (
                    candidate.region_index
                    if candidate.region_index is not None
                    else -1
                ),
                "region_type": getattr(
                    candidate,
                    "region_type",
                    None,
                ),
                "path": list(path),
                "scores": decision_score.as_dict(),
            }

            self.decision_history.append(decision_record)

            return (
                decision_score.total,
                context_region_priority,
                trajectory_region_priority,
                context_rule_priority,
                transition_score,
                decision_score.context,
                decision_score.failure,
                decision_score.graph,
                decision_score.learned,
                decision_score.trajectory,
                (
                    candidate.region_index
                    if candidate.region_index is not None
                    else -1
                ),
                candidate.name,
            )

        graph_score = (
            self.graph_guidance.score_candidate(
                candidate,
                path
            )
            if self.graph_guidance is not None
            else 0.0
        )

        context_guidance_score = (
            self.context_guidance.candidate_score(
                self._current_code,
                candidate,
                path,
            )
            if self.context_guidance is not None
            else 0.0
        )

        failure_guidance_score = (
            self.failure_guidance.score_candidate(
                candidate,
                current_code=self._current_code,
            )
            if self.failure_guidance is not None
            else 0.0
        )

        return (
            context_region_priority,
            trajectory_region_priority,
            context_rule_priority,
            transition_score,
            context_guidance_score,
            failure_guidance_score,
            graph_score,
            learned_score,
            (
                candidate.region_index
                if candidate.region_index is not None
                else -1
            ),
            candidate.name,
        )

    def _node_score(self, node_id):
        """
        Recupera o último score de avaliação associado a um nó de código.
        O nó inicial pode não possuir avaliação; nesse caso, seu score é 0.0.
        """
        node = self.graph.nodes.get(node_id)
        if not node:
            return 0.0

        scores = []

        for edge in self.graph.edges:
            if (
                edge.get("source") == node_id
                and edge.get("relation") == "evaluated_by"
            ):
                evaluation = self.graph.nodes.get(edge.get("target"))
                if not evaluation:
                    continue

                data = evaluation.get("data", {})

                try:
                    scores.append(float(data.get("score", 0.0)))
                except (TypeError, ValueError):
                    continue

        if not scores:
            return 0.0

        return scores[-1]

    def _materialize_candidate(
        self,
        source_id,
        candidate,
    ):
        source = self.graph.nodes[source_id]

        source_code = source["data"].get(
            "code",
            ""
        )

        new_code = candidate.code()

        result = self.evaluator(
            new_code
        )

        node_id = None

        if new_code != source_code:
            node_id = f"path_candidate_{len(self.graph.nodes):04d}"

            if node_id not in self.graph.nodes:
                self.graph.add_node(
                    node_id,
                    "code",
                    {
                        "code": new_code,
                        "language": "python",
                        "generated_by": candidate.name,
                        "source_node": source_id,
                        "region_index": candidate.region_index,
                        "region_type": candidate.region_type,
                    },
                )

                self.graph.connect(
                    source_id,
                    node_id,
                    candidate.name,
                )


        # Registro automático da tentativa no grafo.
        # Cada candidato avaliado passa a produzir uma
        # evidência persistente de sucesso ou falha.
        if node_id is not None:
            evaluation = Evaluation(
                success=bool(result.get("success", False)),
                score=float(result.get("score", 0.0)),
                reason=result.get("reason", ""),
            )

            record_evaluation(
                self.graph,
                node_id,
                evaluation,
            )

        return {
            "candidate": candidate,
            "source_id": source_id,
            "source_code": source_code,
            "code": new_code,
            "node_id": node_id,
            **result,
        }

    def search(
        self,
        source_id,
    ):
        source = self.graph.nodes.get(
            source_id
        )

        if not source:
            raise ValueError(
                f"Nó de origem não existe: {source_id}"
            )

        source_code = source["data"].get(
            "code",
            ""
        )

        self._current_code = source_code

        frontier = [
            {
                "node_id": source_id,
                "score": 0.0,
                "path": [],
            }
        ]

        seen_codes = {
            source_code
        }

        evaluated_candidates = []
        discarded_candidates = []

        for depth in range(
            1,
            self.max_depth + 1
        ):
            next_frontier = []

            for state in frontier:
                current_node_id = state["node_id"]

                current_node = self.graph.nodes.get(
                    current_node_id
                )

                if not current_node:
                    continue

                current_code = current_node[
                    "data"
                ].get(
                    "code",
                    ""
                )

                self._current_code = current_code

                candidates = self.mutator.generate(
                    current_code
                )

                if self.transition_memory is not None:
                    before = len(candidates)

                    candidates = (
                        self.transition_memory.filter_candidates(
                            current_code,
                            candidates
                        )
                    )

                    discarded_candidates.extend(
                        [
                            candidate.name
                            for candidate in []
                        ]
                    )

                    _ = before

                if self.use_pruner and self.region_pruner:
                    candidates = (
                        self.region_pruner.filter(
                            current_code,
                            candidates
                        )
                    )

                candidates.sort(
                    key=lambda candidate:
                        self._candidate_sort_key(
                            state["path"],
                            candidate
                        ),
                    reverse=True,
                )

                # Avalia o estado atual antes de medir a melhoria
                # produzida por cada mutação.
                if not any(
                    edge.get("source") == current_node_id
                    and edge.get("relation") == "evaluated_by"
                    for edge in self.graph.edges
                ):
                    current_node = self.graph.nodes.get(
                        current_node_id
                    )

                    if current_node:
                        current_code = (
                            current_node.get("data", {})
                            .get("code", "")
                        )

                        if current_code:
                            current_result = self.evaluator(
                                current_code
                            )

                            current_score = float(
                                current_result.get(
                                    "score",
                                    0.0,
                                )
                            )

                            evaluation = Evaluation(
                                success=bool(
                                    current_result.get(
                                        "success",
                                        False,
                                    )
                                ),
                                score=current_score,
                                reason=current_result.get(
                                    "reason",
                                    "",
                                ),
                            )

                            record_evaluation(
                                self.graph,
                                current_node_id,
                                evaluation,
                            )

                for candidate in candidates:
                    result = (
                        self._materialize_candidate(
                            current_node_id,
                            candidate
                        )
                    )

                    parent_score = self._node_score(
                        current_node_id
                    )

                    candidate_score = float(
                        result.get("score", 0.0)
                    )

                    fitness_delta = (
                        candidate_score - parent_score
                    )

                    if (
                        self.use_decision_score
                        and result.get("node_id")
                    ):
                        decision_score = (
                            self._decision_score_for_candidate(
                                state["path"],
                                candidate,
                            )
                        )

                        decision_score.fitness_delta = (
                            fitness_delta
                        )

                        problem_id = (
                            self.decision_recorder.find_problem_id(
                                current_node_id
                            )
                        )

                        outcome = (
                            "success"
                            if result.get("success")
                            else "failure"
                        )

                        decision_node = self.decision_recorder.record(
                            problem_id=problem_id,
                            candidate=candidate,
                            decision_score=decision_score,
                            path=state["path"],
                            selected=bool(
                                result.get("success")
                            ),
                            candidate_node_id=result.get(
                                "node_id"
                            ),
                            outcome=outcome,
                            source_code=result.get(
                                "source_code",
                                "",
                            ),
                        )

                        if decision_node:
                            self.search_decision_ids.append(
                                decision_node["id"]
                            )

                    evaluated_candidates.append(
                        {
                            "depth": depth,
                            "source": current_node_id,
                            "candidate": candidate.name,
                            "region_index": (
                                candidate.region_index
                            ),
                            "region_type": (
                                candidate.region_type
                            ),
                            "success": result["success"],
                            "score": result["score"],
                            "reason": result.get(
                                "reason",
                                ""
                            ),
                        }
                    )

                    if result["code"] in seen_codes:
                        continue

                    seen_codes.add(
                        result["code"]
                    )

                    if result["success"]:
                        successful_path = (
                            state["path"]
                            + [candidate.name]
                        )

                        credited_decisions = (
                            self._record_trajectory_credit(
                                successful_path
                            )
                        )

                        return {
                            "success": True,
                            "score": result["score"],
                            "path": successful_path,
                            "credited_decisions": (
                                credited_decisions
                            ),
                            "region_path": [
                                {
                                    "rule": step["rule"],
                                    "region_index": step.get(
                                        "region_index"
                                    ),
                                    "region_type": step.get(
                                        "region_type"
                                    ),
                                }
                                for step in (
                                    state.get(
                                        "region_path",
                                        []
                                    )
                                )
                            ]
                            + [
                                {
                                    "rule": candidate.name,
                                    "region_index": (
                                        candidate.region_index
                                    ),
                                    "region_type": (
                                        candidate.region_type
                                    ),
                                }
                            ],
                            "node_id": result["node_id"],
                            "evaluated_candidates": (
                                evaluated_candidates
                            ),
                            "discarded_candidates": (
                                discarded_candidates
                            ),
                        }

                    if result["score"] >= 0 and result.get("node_id"):
                        next_frontier.append(
                            {
                                "node_id": result["node_id"],
                                "score": result["score"],
                                "path": state["path"]
                                + [candidate.name],
                                "region_path": state.get(
                                    "region_path",
                                    []
                                )
                                + [
                                    {
                                        "rule": candidate.name,
                                        "region_index": (
                                            candidate.region_index
                                        ),
                                        "region_type": (
                                            candidate.region_type
                                        ),
                                    }
                                ],
                            }
                        )

            next_frontier.sort(
                key=lambda item: (
                    item["score"],
                    -len(item["path"]),
                ),
                reverse=True,
            )

            frontier = next_frontier[
                :self.beam_width
            ]

            if not frontier:
                break

        return {
            "success": False,
            "score": 0.0,
            "path": [],
            "region_path": [],
            "node_id": None,
            "evaluated_candidates": (
                evaluated_candidates
            ),
            "discarded_candidates": (
                discarded_candidates
            ),
        }
