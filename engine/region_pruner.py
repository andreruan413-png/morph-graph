from engine.region_selector import RegionSelector


class RegionPruner:
    """
    Controla exploração de mutações usando regiões estruturais.

    A ideia não é eliminar completamente mutações desconhecidas.
    Mantemos uma parcela delas para exploração.
    """

    def __init__(
        self,
        graph,
        exploration_rate=0.25,
    ):
        self.graph = graph
        self.selector = RegionSelector(graph)
        self.exploration_rate = exploration_rate

    def rank(
        self,
        source_code,
        candidates,
    ):
        selection = self.selector.select(source_code)

        rule_priorities = selection.get(
            "priorities",
            {}
        )

        region_priorities = selection.get(
            "region_priorities",
            {}
        )

        def candidate_score(candidate):
            rule_score = rule_priorities.get(
                candidate.name,
                0,
            )

            # Mutations over BinOp are currently the most
            # directly related to the learned arithmetic domain.
            region_score = 0

            name = candidate.name

            if "binop_" in name:
                region_score = max(
                    region_priorities.values(),
                    default=0,
                )

            return (
                rule_score,
                region_score,
                candidate.name,
            )

        return sorted(
            candidates,
            key=candidate_score,
            reverse=True,
        )

    def filter(
        self,
        source_code,
        candidates,
    ):
        ranked = self.rank(
            source_code,
            candidates,
        )

        if not ranked:
            return []

        selection = self.selector.select(
            source_code
        )

        learned_rules = set(
            selection.get(
                "priorities",
                {}
            ).keys()
        )

        learned = [
            candidate
            for candidate in ranked
            if candidate.name in learned_rules
        ]

        unknown = [
            candidate
            for candidate in ranked
            if candidate.name not in learned_rules
        ]

        if not learned:
            return ranked

        if not unknown:
            return learned

        exploration_count = max(
            1,
            int(
                len(unknown)
                * self.exploration_rate
            ),
        )

        return (
            learned
            + unknown[:exploration_count]
        )

    def promising_rules(self, source_code):
        selection = self.selector.select(
            source_code
        )

        return list(
            selection.get(
                "priorities",
                {}
            ).keys()
        )

    def promising_regions(self, source_code):
        return self.selector.promising_regions(
            source_code
        )
