from collections import defaultdict


class GraphGuidance:
    """
    Usa a estrutura do grafo para priorizar candidatos.

    A ideia é transformar relações históricas do grafo em
    sinais de prioridade para a próxima busca.
    """

    def __init__(self, graph, problem_id=None):
        self.graph = graph
        self.problem_id = problem_id

    def _experiences(self):
        return [
            node for node in self.graph.nodes.values()
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
                if (
                    self.problem_id is not None
                    and data.get("problem_id") != self.problem_id
                ):
                    continue
                result.append(experience)

        return result

    def _trajectory(self, experience):
        return experience.get("data", {}).get("trajectory", [])

    def rule_scores(self):
        """
        Conta quantas experiências bem-sucedidas utilizaram cada regra.
        """
        scores = defaultdict(float)

        for experience in self._successful_experiences():
            trajectory = self._trajectory(experience)

            for step in trajectory:
                rule = step.get("rule")

                if rule:
                    scores[rule] += 1.0

        return dict(scores)

    def region_scores(self):
        """
        Conta quais regiões apareceram em trajetórias bem-sucedidas.
        """
        scores = defaultdict(float)

        for experience in self._successful_experiences():
            trajectory = self._trajectory(experience)

            for step in trajectory:
                rule = step.get("rule")
                region_index = step.get("region_index")
                region_type = step.get("region_type")

                if rule:
                    key = (rule, region_index, region_type)
                    scores[key] += 1.0

        return dict(scores)

    def transition_scores(self):
        """
        Aprende relações entre transformações consecutivas.

        Exemplo:

        A -> B -> C

        gera:

        A -> B
        B -> C
        """
        scores = defaultdict(float)

        for experience in self._successful_experiences():
            trajectory = self._trajectory(experience)

            rules = [
                step.get("rule")
                for step in trajectory
                if step.get("rule")
            ]

            for current_rule, next_rule in zip(rules, rules[1:]):
                scores[(current_rule, next_rule)] += 1.0

        return dict(scores)

    def score_candidate(self, candidate, path):
        """
        Calcula a prioridade de um candidato considerando:

        1. regra já usada com sucesso;
        2. região usada com sucesso;
        3. transição que costuma vir depois do caminho atual.
        """

        rule = getattr(candidate, "name", None)
        region_index = getattr(candidate, "region_index", None)
        region_type = getattr(candidate, "region_type", None)

        if not rule:
            return 0.0

        score = 0.0

        rules = self.rule_scores()
        regions = self.region_scores()
        transitions = self.transition_scores()

        # Regra já comprovada.
        score += rules.get(rule, 0.0) * 10.0

        # Regra + região já comprovadas.
        region_key = (rule, region_index, region_type)
        score += regions.get(region_key, 0.0) * 5.0

        # Próxima transformação provável.
        if path:
            previous_rule = path[-1]

            score += transitions.get(
                (previous_rule, rule),
                0.0
            ) * 20.0

        return score

    def rank(self, candidates, path=None):
        """
        Retorna candidatos ordenados pela evidência existente no grafo.
        """

        path = path or []

        ranked = []

        for candidate in candidates:
            score = self.score_candidate(candidate, path)

            ranked.append({
                "candidate": candidate,
                "name": getattr(candidate, "name", None),
                "region_index": getattr(
                    candidate,
                    "region_index",
                    None
                ),
                "region_type": getattr(
                    candidate,
                    "region_type",
                    None
                ),
                "graph_score": score,
            })

        ranked.sort(
            key=lambda item: item["graph_score"],
            reverse=True
        )

        return ranked
