import ast

from engine.structure import structural_profile, structural_similarity
from engine.trajectory_memory import TrajectoryMemory


class RegionSelector:
    """
    Seleciona regiões estruturais de um programa com base em:
    - estrutura AST;
    - experiências anteriores;
    - regiões que participaram de trajetórias bem-sucedidas.
    """

    def __init__(self, graph):
        self.graph = graph
        self.trajectory_memory = TrajectoryMemory(graph)

    def _regions(self, code):
        tree = ast.parse(code)
        regions = []

        for index, node in enumerate(ast.walk(tree)):
            if isinstance(node, (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.Return,
                ast.BinOp,
                ast.Call,
                ast.Assign,
                ast.Tuple,
            )):
                regions.append({
                    "index": index,
                    "type": type(node).__name__,
                    "lineno": getattr(node, "lineno", None),
                    "col_offset": getattr(node, "col_offset", None),
                })

        return regions

    def _experience_codes(self):
        results = []

        for experience in self.trajectory_memory._experiences():
            data = experience["data"]

            solution_id = data.get("solution_node")
            if not solution_id:
                continue

            solution = self.graph.nodes.get(solution_id)
            if not solution:
                continue

            if solution["type"] != "code":
                continue

            code = solution["data"].get("code", "")
            if not code:
                continue

            results.append({
                "experience_id": experience["id"],
                "code": code,
                "path": self._path(experience),
            })

        return results

    def _path(self, experience):
        path = []

        for generation in experience["data"].get("generations", []):
            selected = generation.get("selected", {})
            rule = selected.get("rule")

            if rule:
                path.append(rule)

        return path

    def rank_experiences(self, source_code):
        source_profile = structural_profile(source_code)
        ranked = []

        for item in self._experience_codes():
            similarity = structural_similarity(
                source_profile,
                structural_profile(item["code"])
            )

            ranked.append({
                "experience_id": item["experience_id"],
                "similarity": similarity,
                "path": item["path"],
                "code": item["code"],
            })

        ranked.sort(
            key=lambda item: (
                item["similarity"],
                len(item["path"]),
            ),
            reverse=True,
        )

        return ranked

    def select(self, source_code):
        ranked = self.rank_experiences(source_code)

        regions = self._regions(source_code)

        if not ranked:
            return {
                "selected": None,
                "experiences": [],
                "priorities": {},
                "regions": regions,
            }

        selected = ranked[0]

        rule_priorities = {}

        for index, rule in enumerate(selected["path"]):
            rule_priorities[rule] = (
                len(selected["path"]) - index
            )

        # A região recebe uma prioridade baseada na posição
        # das operações aprendidas. Isso cria uma representação
        # explícita de "onde" a transformação ocorreu.
        region_priorities = {}

        for region in regions:
            score = 0.0

            if region["type"] == "BinOp":
                score += 1.0

            if region["type"] == "Return":
                score += 0.5

            if region["type"] == "FunctionDef":
                score += 0.25

            region_priorities[region["index"]] = score

        return {
            "selected": selected,
            "experiences": ranked,
            "priorities": rule_priorities,
            "region_priorities": region_priorities,
            "regions": regions,
        }

    def promising_regions(self, source_code):
        selection = self.select(source_code)

        priorities = selection.get(
            "region_priorities",
            {}
        )

        return sorted(
            priorities.items(),
            key=lambda item: item[1],
            reverse=True,
        )
