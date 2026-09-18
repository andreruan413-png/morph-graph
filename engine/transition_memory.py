import json

from engine.memory import code_signature


class TransitionMemory:

    def __init__(self, graph):
        self.graph = graph

        # Memória de transições:
        #
        # assinatura_origem
        #     -> mutação
        #     -> quantidade de sucessos
        #
        self.persistent = {}

        # Agora uma assinatura pode possuir
        # várias trajetórias.
        #
        # assinatura
        #     -> [
        #          {
        #              "path": [...],
        #              "count": N,
        #              "score": X
        #          }
        #        ]
        #
        self.trajectories = {}

        # Memória de transições individuais:
        #
        # assinatura atual
        #     -> {
        #          mutation,
        #          target_signature
        #        }
        #
        self.trajectory_steps = {}

    # ---------------------------------------------------------
    # TRANSIÇÕES OBSERVADAS NO GRAFO
    # ---------------------------------------------------------

    def transitions(self):

        results = []

        for item in self.graph.history:

            if item.get("action") != "path_transform":
                continue

            source_id = item.get("source")
            target_id = item.get("target")
            mutation = item.get("rule")

            source = self.graph.nodes.get(
                source_id
            )

            target = self.graph.nodes.get(
                target_id
            )

            if not source or not target:
                continue

            if source.get("type") != "code":
                continue

            if target.get("type") != "code":
                continue

            source_code = source["data"].get(
                "code",
                ""
            )

            target_code = target["data"].get(
                "code",
                ""
            )

            if not source_code or not target_code:
                continue

            evaluation = None

            for node in self.graph.nodes.values():

                if node.get("type") != "evaluation":
                    continue

                data = node.get(
                    "data",
                    {}
                )

                if data.get(
                    "target_node"
                ) == target_id:

                    evaluation = data
                    break

            success = False

            if evaluation:
                success = bool(
                    evaluation.get(
                        "success",
                        False
                    )
                )

            results.append({
                "source_id": source_id,
                "target_id": target_id,
                "source_signature": code_signature(
                    source_code
                ),
                "target_signature": code_signature(
                    target_code
                ),
                "mutation": mutation,
                "success": success
            })

        return results

    # ---------------------------------------------------------
    # MUTAÇÕES BEM-SUCEDIDAS
    # ---------------------------------------------------------

    def successful_mutations(
        self,
        source_code
    ):

        signature = code_signature(
            source_code
        )

        return [
            transition
            for transition in self.transitions()
            if (
                transition[
                    "source_signature"
                ] == signature
                and transition[
                    "success"
                ]
            )
        ]

    # ---------------------------------------------------------
    # REGISTRAR TRAJETÓRIA
    # ---------------------------------------------------------

    def record_trajectory(
        self,
        source_code,
        path,
        score=1.0
    ):

        if not path:
            return []

        signature = code_signature(
            source_code
        )

        path = list(path)

        trajectories = self.trajectories.setdefault(
            signature,
            []
        )

        # Procuramos uma trajetória idêntica.
        for trajectory in trajectories:

            if trajectory.get(
                "path"
            ) == path:

                trajectory["count"] = (
                    int(
                        trajectory.get(
                            "count",
                            1
                        )
                    )
                    + 1
                )

                trajectory["score"] = max(
                    float(
                        trajectory.get(
                            "score",
                            0.0
                        )
                    ),
                    float(score)
                )

                return trajectories

        # Trajetória nova.
        trajectories.append({
            "path": path,
            "count": 1,
            "score": float(score)
        })

        return trajectories

    # ---------------------------------------------------------
    # REGISTRAR RESULTADO DA BUSCA
    # ---------------------------------------------------------

    def record_search_result(
        self,
        source_id,
        path
    ):

        if not path:
            return {}

        source = self.graph.nodes.get(
            source_id
        )

        if not source:
            return {}

        if source.get("type") != "code":
            return {}

        current_id = source_id

        steps = {}

        for mutation in path:

            current = self.graph.nodes.get(
                current_id
            )

            if not current:
                break

            if current.get(
                "type"
            ) != "code":
                break

            current_code = current[
                "data"
            ].get(
                "code",
                ""
            )

            if not current_code:
                break

            current_signature = code_signature(
                current_code
            )

            target = None

            for node_id, node in self.graph.nodes.items():

                if node_id == current_id:
                    continue

                if node.get(
                    "type"
                ) != "code":
                    continue

                data = node.get(
                    "data",
                    {}
                )

                if data.get(
                    "source_node"
                ) != current_id:
                    continue

                if data.get(
                    "generated_by"
                ) != mutation:
                    continue

                target = node
                break

            if target is None:
                break

            target_code = target[
                "data"
            ].get(
                "code",
                ""
            )

            if not target_code:
                break

            target_signature = code_signature(
                target_code
            )

            steps[current_signature] = {
                "mutation": mutation,
                "target_signature": target_signature
            }

            current_id = target["id"]

        self.trajectory_steps.update(
            steps
        )

        return steps

    # ---------------------------------------------------------
    # PRIORIDADES DE MUTAÇÃO
    # ---------------------------------------------------------

    def mutation_priority(
        self,
        source_code
    ):

        signature = code_signature(
            source_code
        )

        priorities = {}

        # -----------------------------------------------------
        # MEMÓRIA PERSISTENTE DE TRANSIÇÕES
        # -----------------------------------------------------

        persistent = self.persistent.get(
            signature,
            {}
        )

        if isinstance(
            persistent,
            dict
        ):

            for mutation, count in persistent.items():

                if mutation.startswith("_"):
                    continue

                priorities[mutation] = (
                    priorities.get(
                        mutation,
                        0
                    )
                    + int(count)
                )

        # -----------------------------------------------------
        # TODAS AS TRAJETÓRIAS CONHECIDAS
        # -----------------------------------------------------

        trajectories = self.trajectories.get(
            signature,
            []
        )

        if isinstance(
            trajectories,
            list
        ):

            for trajectory in trajectories:

                if not isinstance(
                    trajectory,
                    dict
                ):
                    continue

                path = trajectory.get(
                    "path",
                    []
                )

                count = int(
                    trajectory.get(
                        "count",
                        1
                    )
                )

                score = float(
                    trajectory.get(
                        "score",
                        1.0
                    )
                )

                if not path:
                    continue

                first_step = path[0]

                priorities[first_step] = (
                    priorities.get(
                        first_step,
                        0
                    )
                    + 100
                    * count
                    * max(
                        score,
                        0.0
                    )
                )

        # -----------------------------------------------------
        # PRÓXIMO PASSO APRENDIDO
        # -----------------------------------------------------

        step = self.trajectory_steps.get(
            signature
        )

        if isinstance(
            step,
            dict
        ):

            mutation = step.get(
                "mutation"
            )

            if mutation:

                priorities[mutation] = (
                    priorities.get(
                        mutation,
                        0
                    )
                    + 100
                )

        # -----------------------------------------------------
        # TRANSIÇÕES BEM-SUCEDIDAS DO GRAFO
        # -----------------------------------------------------

        for transition in self.successful_mutations(
            source_code
        ):

            mutation = transition[
                "mutation"
            ]

            priorities[mutation] = (
                priorities.get(
                    mutation,
                    0
                )
                + 1
            )

        return dict(
            sorted(
                priorities.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

    # ---------------------------------------------------------
    # MELHOR PRÓXIMO PASSO
    # ---------------------------------------------------------

    def learned_next_step(
        self,
        source_code
    ):

        priorities = self.mutation_priority(
            source_code
        )

        if not priorities:
            return None

        return next(
            iter(priorities)
        )

    # ---------------------------------------------------------
    # FILTRO DE CANDIDATOS
    # ---------------------------------------------------------

    def filter_candidates(
        self,
        source_code,
        candidates,
        exploration_rate=0.25
    ):

        candidates = list(
            candidates
        )

        if not candidates:
            return []

        priorities = self.mutation_priority(
            source_code
        )

        if not priorities:
            return candidates

        learned = []
        unknown = []

        learned_names = set(
            priorities.keys()
        )

        for candidate in candidates:

            if candidate.name in learned_names:
                learned.append(
                    candidate
                )

            else:
                unknown.append(
                    candidate
                )

        learned.sort(
            key=lambda candidate:
                priorities.get(
                    candidate.name,
                    0
                ),
            reverse=True
        )

        unknown.sort(
            key=lambda candidate:
                candidate.name
        )

        if not unknown:
            return learned

        exploration_count = max(
            1,
            int(
                len(unknown)
                * exploration_rate
            )
        )

        exploration = unknown[
            :exploration_count
        ]

        return learned + exploration

    # ---------------------------------------------------------
    # EXPORTAÇÃO
    # ---------------------------------------------------------

    def export(
        self,
        path
    ):

        memory = {}

        # -----------------------------------------------------
        # TRANSIÇÕES BEM-SUCEDIDAS
        # -----------------------------------------------------

        for transition in self.transitions():

            if not transition[
                "success"
            ]:
                continue

            signature = transition[
                "source_signature"
            ]

            mutation = transition[
                "mutation"
            ]

            if signature not in memory:

                memory[signature] = {}

            memory[signature][mutation] = (
                memory[signature].get(
                    mutation,
                    0
                )
                + 1
            )

        # -----------------------------------------------------
        # TRAJETÓRIAS
        # -----------------------------------------------------

        if self.trajectories:

            memory[
                "_trajectories"
            ] = self.trajectories

        # -----------------------------------------------------
        # PASSOS INDIVIDUAIS
        # -----------------------------------------------------

        if self.trajectory_steps:

            memory[
                "_trajectory_steps"
            ] = self.trajectory_steps

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                indent=2,
                ensure_ascii=False
            )

        return memory

    # ---------------------------------------------------------
    # NORMALIZAÇÃO DE TRAJETÓRIAS ANTIGAS
    # ---------------------------------------------------------

    def _normalize_loaded_trajectories(
        self,
        data
    ):

        normalized = {}

        for signature, value in data.items():

            # Formato antigo:
            #
            # signature:
            #   ["rule_a", "rule_b"]
            #
            if isinstance(
                value,
                list
            ):

                # Pode ser uma trajetória antiga
                # ou uma lista de trajetórias novas.

                if value and all(
                    isinstance(
                        item,
                        str
                    )
                    for item in value
                ):

                    normalized[signature] = [{
                        "path": list(value),
                        "count": 1,
                        "score": 1.0
                    }]

                    continue

                # Formato:
                #
                # [
                #   {
                #      "path": [...]
                #   }
                # ]
                #

                trajectories = []

                for item in value:

                    if isinstance(
                        item,
                        dict
                    ):

                        path = item.get(
                            "path",
                            []
                        )

                        if path:

                            trajectories.append({
                                "path": list(path),
                                "count": int(
                                    item.get(
                                        "count",
                                        1
                                    )
                                ),
                                "score": float(
                                    item.get(
                                        "score",
                                        1.0
                                    )
                                )
                            })

                normalized[signature] = trajectories

        return normalized

    # ---------------------------------------------------------
    # IMPORTAÇÃO
    # ---------------------------------------------------------

    def load(
        self,
        path
    ):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        trajectories = data.pop(
            "_trajectories",
            {}
        )

        self.trajectory_steps = data.pop(
            "_trajectory_steps",
            {}
        )

        self.trajectories = (
            self._normalize_loaded_trajectories(
                trajectories
            )
        )

        self.persistent = data

        return self.persistent

    # ---------------------------------------------------------
    # CONSULTA DE TRAJETÓRIAS
    # ---------------------------------------------------------

    def known_trajectories(
        self,
        source_code
    ):

        signature = code_signature(
            source_code
        )

        trajectories = self.trajectories.get(
            signature,
            []
        )

        return sorted(
            trajectories,
            key=lambda item: (
                float(
                    item.get(
                        "score",
                        0.0
                    )
                ),
                int(
                    item.get(
                        "count",
                        1
                    )
                ),
                -len(
                    item.get(
                        "path",
                        []
                    )
                )
            ),
            reverse=True
        )

    # ---------------------------------------------------------
    # PRÓXIMOS PASSOS DAS TRAJETÓRIAS
    # ---------------------------------------------------------

    def next_steps(
        self,
        source_code,
        prefix=None
    ):

        signature = code_signature(
            source_code
        )

        trajectories = self.trajectories.get(
            signature,
            []
        )

        if prefix is None:
            prefix = []

        prefix = list(
            prefix
        )

        suggestions = {}

        for trajectory in trajectories:

            path = trajectory.get(
                "path",
                []
            )

            count = int(
                trajectory.get(
                    "count",
                    1
                )
            )

            score = float(
                trajectory.get(
                    "score",
                    1.0
                )
            )

            if len(path) <= len(prefix):
                continue

            if path[:len(prefix)] != prefix:
                continue

            next_rule = path[
                len(prefix)
            ]

            weight = (
                count
                * max(
                    score,
                    0.0
                )
            )

            suggestions[next_rule] = (
                suggestions.get(
                    next_rule,
                    0
                )
                + weight
            )

        return dict(
            sorted(
                suggestions.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
