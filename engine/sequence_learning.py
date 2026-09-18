from collections import defaultdict


class SequenceLearning:
    """
    Aprende sequências de transformações usando a estrutura
    das decisões e a linhagem exata de cada etapa.

    A identidade estrutural de uma transformação é:

        (region_index, region_type, mutation_type)

    A identidade textual do candidato continua existindo,
    mas não é usada para descobrir ambiguamente etapas anteriores.
    """

    def __init__(self, graph):
        self.graph = graph

    def _decisions(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node.get("type") == "decision"
        ]

    def _useful_decisions(self):
        return [
            node
            for node in self._decisions()
            if node.get("data", {}).get("useful") is True
        ]

    def _step_signature(self, decision):
        data = decision.get("data", {})

        return (
            data.get("region_index"),
            data.get("region_type"),
            data.get("mutation_type"),
        )

    def _decision_problem(self, decision):
        return decision.get("data", {}).get("problem_id")

    def _decision_path(self, decision):
        return tuple(
            decision.get("data", {}).get("path", [])
        )

    def _find_lineage_decision(
        self,
        problem_id,
        candidate_name,
        expected_path,
    ):
        """
        Encontra a decisão exata de uma etapa anterior.

        Não basta procurar pelo nome do candidato.
        A decisão também precisa pertencer ao mesmo problema
        e possuir exatamente o caminho esperado.
        """

        for decision in self._useful_decisions():
            data = decision.get("data", {})

            if data.get("problem_id") != problem_id:
                continue

            if data.get("candidate") != candidate_name:
                continue

            path = tuple(data.get("path", []))

            if path == tuple(expected_path):
                return decision

        return None

    def _structural_context(self, decision):
        data = decision.get("data", {})
        problem_id = data.get("problem_id")
        path = list(data.get("path", []))

        context_signatures = []

        for index, previous_candidate in enumerate(path):
            expected_path = path[:index]

            previous = self._find_lineage_decision(
                problem_id,
                previous_candidate,
                expected_path,
            )

            if previous is None:
                context_signatures.append(
                    ("unknown", previous_candidate)
                )
                continue

            context_signatures.append(
                self._step_signature(previous)
            )

        return tuple(context_signatures)

    def _decision_steps(self):
        steps = []

        for decision in self._useful_decisions():
            steps.append(
                (
                    decision,
                    self._step_signature(decision),
                )
            )

        return steps

    def learn(self):
        sequences = defaultdict(
            lambda: defaultdict(float)
        )

        for decision in self._useful_decisions():
            data = decision.get("data", {})
            candidate = data.get("candidate")

            if not candidate:
                continue

            path = tuple(
                data.get("path", [])
            )

            sequences[path][candidate] += 1.0

        return {
            context: dict(candidates)
            for context, candidates in sequences.items()
        }

    def structural_learn(self):
        """
        Aprende transições entre assinaturas estruturais.

        Exemplo:

            () ->
                (0, binop, operator_change)

            ((0, binop, operator_change),) ->
                (1, binop, operator_change)

        Os nomes dos candidatos não participam da identidade
        estrutural da sequência.
        """

        sequences = defaultdict(
            lambda: defaultdict(float)
        )

        decisions = self._useful_decisions()

        for decision in decisions:
            signature = self._step_signature(
                decision
            )

            if signature == (
                None,
                None,
                None,
            ):
                continue

            context = self._structural_context(
                decision
            )

            sequences[context][signature] += 1.0

        return {
            context: dict(candidates)
            for context, candidates in sequences.items()
        }

    def sequence_similarity(self, path_a, path_b):
        a = tuple(path_a)
        b = tuple(path_b)

        if not a and not b:
            return 1.0

        if not a or not b:
            return 0.0

        max_length = max(
            len(a),
            len(b)
        )

        matches = sum(
            1
            for left, right in zip(a, b)
            if left == right
        )

        return matches / max_length

    def structural_similarity(
        self,
        signature_a,
        signature_b,
    ):
        if signature_a == signature_b:
            return 1.0

        if not signature_a or not signature_b:
            return 0.0

        if len(signature_a) != len(signature_b):
            return 0.0

        matches = sum(
            1
            for left, right in zip(
                signature_a,
                signature_b,
            )
            if left == right
        )

        return matches / len(signature_a)

    def generalized_structural_score(
        self,
        path_signatures,
        candidate_signature,
        min_similarity=0.5,
    ):
        if candidate_signature is None:
            return 0.0

        learned = self.structural_learn()

        total = 0.0

        for learned_context, candidates in learned.items():
            similarity = self.sequence_similarity(
                path_signatures,
                learned_context,
            )

            if similarity < min_similarity:
                continue

            for learned_candidate, evidence in candidates.items():
                candidate_similarity = (
                    self.structural_similarity(
                        candidate_signature,
                        learned_candidate,
                    )
                )

                if candidate_similarity < min_similarity:
                    continue

                total += (
                    evidence
                    * similarity
                    * candidate_similarity
                )

        return float(total)

    def score_structural(
        self,
        path_signatures,
        candidate_signature,
    ):
        return self.generalized_structural_score(
            path_signatures,
            candidate_signature,
            min_similarity=0.5,
        )

    def generalized_score(
        self,
        path,
        candidate,
        min_similarity=0.5,
    ):
        if candidate is None:
            return 0.0

        learned = self.learn()

        total = 0.0

        for learned_context, candidates in learned.items():
            similarity = self.sequence_similarity(
                path,
                learned_context,
            )

            if similarity < min_similarity:
                continue

            evidence = candidates.get(
                candidate,
                0.0
            )

            if evidence <= 0.0:
                continue

            total += (
                evidence
                * similarity
            )

        return float(total)

    def score(self, path, candidate):
        return self.generalized_score(
            path,
            candidate,
            min_similarity=0.5,
        )

    def rank(self, path, candidates):
        ranked = []

        for candidate in candidates:
            name = getattr(
                candidate,
                "name",
                None,
            )

            ranked.append(
                (
                    self.score(
                        path,
                        name,
                    ),
                    candidate,
                )
            )

        ranked.sort(
            key=lambda item: (
                item[0],
                getattr(
                    item[1],
                    "name",
                    "",
                ),
            ),
            reverse=True,
        )

        return ranked
