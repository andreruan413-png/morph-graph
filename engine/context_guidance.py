from collections import defaultdict

from engine.structure import structural_profile, structural_similarity
from engine.graph_guidance import GraphGuidance


class ContextGuidance:
    """
    Combina:
    - similaridade estrutural do problema;
    - trajetórias bem-sucedidas;
    - regiões modificadas;
    - transições entre transformações.

    O objetivo é transformar experiências semelhantes
    em prioridade para a próxima busca.
    """

    def __init__(self, graph):
        self.graph = graph
        self.graph_guidance = GraphGuidance(graph)

    def _experiences(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node.get("type") == "experience"
        ]

    def _successful_experiences(self):
        result = []

        for experience in self._experiences():
            try:
                score = float(
                    experience.get("data", {}).get("score", 0.0)
                )
            except (TypeError, ValueError):
                score = 0.0

            if score >= 1.0:
                result.append(experience)

        return result

    def _experience_code(self, experience):
        data = experience.get("data", {})

        # Preferência: código explicitamente registrado
        # no momento em que a experiência foi criada.
        source_code = data.get("source_code")

        if source_code:
            return source_code

        # Compatibilidade com experiências antigas.
        solution_node = data.get("solution_node")

        if solution_node:
            node = self.graph.nodes.get(solution_node)

            if node:
                return node.get("data", {}).get("code", "")

        problem_id = data.get("problem_id")

        if problem_id:
            problem = self.graph.nodes.get(problem_id)

            if problem:
                return problem.get("data", {}).get("code", "")

        return ""

    def similarity(self, current_code, experience):
        previous_code = self._experience_code(experience)

        if not previous_code:
            return 0.0

        try:
            current_profile = structural_profile(current_code)
            previous_profile = structural_profile(previous_code)

            return float(
                structural_similarity(
                    current_profile,
                    previous_profile
                )
            )
        except Exception:
            return 0.0

    def rank_experiences(self, current_code):
        ranked = []

        for experience in self._successful_experiences():
            similarity = self.similarity(
                current_code,
                experience
            )

            ranked.append({
                "experience_id": experience["id"],
                "similarity": similarity,
                "score": float(
                    experience.get("data", {}).get(
                        "score",
                        0.0
                    )
                ),
                "trajectory": experience.get(
                    "data", {}
                ).get("trajectory", []),
            })

        ranked.sort(
            key=lambda item: (
                item["similarity"],
                item["score"],
            ),
            reverse=True,
        )

        return ranked

    def _current_problem_ids(self, current_code):
        problem_ids = set()
        for node_id, node in self.graph.nodes.items():
            if not isinstance(node, dict) or node.get("type") != "code":
                continue
            if node.get("data", {}).get("code", "") != current_code:
                continue
            current = node_id
            visited = set()
            while current and current not in visited:
                visited.add(current)
                node_data = self.graph.nodes.get(current, {}).get("data", {})
                parent = node_data.get("source_node")
                if parent:
                    current = parent
                    continue
                for edge in self.graph.edges:
                    if edge.get("target") == current and edge.get("relation") in {"has_candidate", "has_solution"}:
                        current = edge.get("source")
                        break
                else:
                    current = None
            if current and self.graph.nodes.get(current, {}).get("type") == "problem":
                problem_ids.add(current)
        return problem_ids

    def _experience_is_relevant(self, experience_id, problem_ids):
        if not problem_ids:
            return False
        for edge in self.graph.edges:
            if edge.get("source") in problem_ids and edge.get("target") == experience_id and edge.get("relation") in {"has_experience", "produced_experience"}:
                return True
        return False

    def candidate_score(
        self,
        current_code,
        candidate,
        path=None,
    ):
        path = path or []

        score = 0.0
        problem_ids = self._current_problem_ids(current_code)

        experiences = self.rank_experiences(
            current_code
        )

        for experience in experiences:
            if not self._experience_is_relevant(experience["experience_id"], problem_ids):
                continue

            similarity = experience["similarity"]

            if similarity <= 0:
                continue

            trajectory = experience["trajectory"]

            rules = [
                step.get("rule")
                for step in trajectory
                if step.get("rule")
            ]

            if len(rules) <= len(path):
                continue

            if rules[:len(path)] != path:
                continue

            expected = trajectory[len(path)]

            if expected.get("rule") != candidate.name:
                continue

            score += similarity * 100.0

            if (
                expected.get("region_index")
                == getattr(candidate, "region_index", None)
                and
                expected.get("region_type")
                == getattr(candidate, "region_type", None)
            ):
                score += similarity * 50.0

        return score

    def rank(
        self,
        current_code,
        candidates,
        path=None,
    ):
        path = path or []

        ranked = []

        for candidate in candidates:
            ranked.append({
                "candidate": candidate,
                "name": getattr(candidate, "name", None),
                "context_score": self.candidate_score(
                    current_code,
                    candidate,
                    path,
                ),
            })

        ranked.sort(
            key=lambda item: item["context_score"],
            reverse=True,
        )

        return ranked
