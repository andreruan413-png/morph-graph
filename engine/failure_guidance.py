from collections import defaultdict

from engine.structure import structural_profile, structural_similarity


class FailureGuidance:
    """
    Aprende com falhas levando em consideração o contexto
    estrutural do código.

    Uma transformação que falhou em um contexto não deve ser
    automaticamente considerada ruim em todos os contextos.
    """

    def __init__(self, graph):
        self.graph = graph

    def _experiences(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node.get("type") == "experience"
        ]

    def _successful_experiences(self):
        result = []

        for experience in self._experiences():
            data = experience.get("data", {})

            try:
                score = float(data.get("score", 0.0))
            except (TypeError, ValueError):
                score = 0.0

            if score >= 1.0:
                result.append(experience)

        return result

    def _experience_code(self, experience):
        data = experience.get("data", {})

        source_code = data.get("source_code")

        if source_code:
            return source_code

        solution_node = data.get("solution_node")

        if solution_node:
            node = self.graph.nodes.get(solution_node)

            if node:
                return node.get(
                    "data",
                    {}
                ).get(
                    "code",
                    ""
                )

        problem_id = data.get("problem_id")

        if problem_id:
            problem = self.graph.nodes.get(problem_id)

            if problem:
                return problem.get(
                    "data",
                    {}
                ).get(
                    "code",
                    ""
                )

        return ""

    def _failed_evaluations(self):
        failures = []

        for node in self.graph.nodes.values():

            if node.get("type") != "evaluation":
                continue

            data = node.get("data", {})

            if data.get("success"):
                continue

            target_id = data.get("target_node")

            target = self.graph.nodes.get(
                target_id
            )

            if not target:
                continue

            target_data = target.get(
                "data",
                {}
            )

            rule = target_data.get(
                "generated_by"
            )

            if not rule:
                continue

            source_node_id = target_data.get(
                "source_node"
            )

            source_node = self.graph.nodes.get(
                source_node_id
            )

            source_code = ""

            if source_node:
                source_code = source_node.get(
                    "data",
                    {}
                ).get(
                    "code",
                    ""
                )

            failures.append({
                "evaluation_id": node["id"],
                "target_id": target_id,
                "rule": rule,
                "region_index": target_data.get(
                    "region_index"
                ),
                "region_type": target_data.get(
                    "region_type"
                ),
                "source_code": source_code,
                "score": float(
                    data.get(
                        "score",
                        0.0
                    )
                ),
                "reason": data.get(
                    "reason",
                    ""
                ),
            })

        return failures

    def rule_failures(self):
        failures = defaultdict(float)

        for item in self._failed_evaluations():
            failures[item["rule"]] += 1.0

        return dict(failures)

    def region_failures(self):
        failures = defaultdict(float)

        for item in self._failed_evaluations():
            key = (
                item["rule"],
                item["region_index"],
                item["region_type"],
            )

            failures[key] += 1.0

        return dict(failures)

    def contextual_failures(
        self,
        current_code,
        similarity_threshold=0.5,
    ):
        """
        Retorna falhas ponderadas pela semelhança estrutural
        entre o código atual e o código que gerou a falha.
        """

        result = []

        try:
            current_profile = structural_profile(
                current_code
            )
        except Exception:
            return result

        for failure in self._failed_evaluations():

            previous_code = failure.get(
                "source_code",
                ""
            )

            if not previous_code:
                continue

            try:
                previous_profile = structural_profile(
                    previous_code
                )

                similarity = float(
                    structural_similarity(
                        current_profile,
                        previous_profile
                    )
                )

            except Exception:
                similarity = 0.0

            if similarity < similarity_threshold:
                continue

            item = dict(failure)

            item["similarity"] = similarity

            result.append(item)

        result.sort(
            key=lambda item: (
                item["similarity"],
                item["score"],
            ),
            reverse=True,
        )

        return result

    def contextual_rule_failures(
        self,
        current_code,
        similarity_threshold=0.5,
    ):
        """
        Conta falhas da transformação, mas somente quando
        o contexto estrutural é suficientemente semelhante.
        """

        failures = defaultdict(float)

        contextual = self.contextual_failures(
            current_code,
            similarity_threshold,
        )

        for item in contextual:

            rule = item.get("rule")

            similarity = float(
                item.get(
                    "similarity",
                    0.0
                )
            )

            failures[rule] += similarity

        return dict(failures)

    def score_candidate(
        self,
        candidate,
        current_code=None,
        similarity_threshold=0.5,
    ):
        rule = getattr(
            candidate,
            "name",
            None
        )

        if not rule:
            return 0.0

        score = 0.0

        # -------------------------------------------------
        # SEM CONTEXTO:
        # mantém o comportamento anterior.
        # -------------------------------------------------

        if current_code is None:

            failures = self.rule_failures()
            regions = self.region_failures()

            score -= failures.get(
                rule,
                0.0
            ) * 10.0

            region_key = (
                rule,
                getattr(
                    candidate,
                    "region_index",
                    None
                ),
                getattr(
                    candidate,
                    "region_type",
                    None
                ),
            )

            score -= regions.get(
                region_key,
                0.0
            ) * 5.0

            return score

        # -------------------------------------------------
        # COM CONTEXTO:
        # somente falhas estruturalmente semelhantes
        # influenciam a decisão.
        # -------------------------------------------------

        contextual = self.contextual_failures(
            current_code,
            similarity_threshold,
        )

        for failure in contextual:

            if failure.get("rule") != rule:
                continue

            similarity = float(
                failure.get(
                    "similarity",
                    0.0
                )
            )

            score -= similarity * 10.0

            same_region = (
                failure.get("region_index")
                == getattr(
                    candidate,
                    "region_index",
                    None
                )
                and
                failure.get("region_type")
                == getattr(
                    candidate,
                    "region_type",
                    None
                )
            )

            if same_region:
                score -= similarity * 5.0

        return score

    def rank(
        self,
        candidates,
        current_code=None,
        similarity_threshold=0.5,
    ):
        ranked = []

        for candidate in candidates:

            ranked.append({
                "candidate": candidate,
                "name": getattr(
                    candidate,
                    "name",
                    None
                ),
                "failure_score": self.score_candidate(
                    candidate,
                    current_code=current_code,
                    similarity_threshold=similarity_threshold,
                ),
            })

        ranked.sort(
            key=lambda item: item[
                "failure_score"
            ],
            reverse=True,
        )

        return ranked
