import ast
import hashlib


class ContextMemory:
    """
    Memória contextual do MORPH-GRAPH.

    Guarda associações entre:

        contexto
            ↓
        trajetória
            ↓
        regra + região

    A região pode ser um índice AST e seu tipo.
    """

    def __init__(self, graph):
        self.graph = graph

    # =========================================================
    # EXTRAÇÃO DOS TESTES
    # =========================================================

    def _extract_tests(self, tests):
        expressions = []

        for line in tests.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("TEST:"):
                line = line[len("TEST:"):].strip()

            if line.startswith("assert "):
                line = line[len("assert "):].strip()

            if line:
                expressions.append(line)

        return expressions

    # =========================================================
    # AVALIAÇÃO SEGURA DE CONSTANTES
    # =========================================================

    def _literal_value(self, node):
        try:
            return ast.literal_eval(node)
        except Exception:
            return None

    # =========================================================
    # EXTRAIR RELAÇÃO ENTRADA → SAÍDA
    # =========================================================

    def _infer_relation(
        self,
        input_values,
        output_values
    ):
        if len(input_values) < 2:
            return None

        a = input_values[0]
        b = input_values[1]

        if not isinstance(a, (int, float)):
            return None

        if not isinstance(b, (int, float)):
            return None

        operations = {
            "a+b": a + b,
            "a-b": a - b,
            "b-a": b - a,
            "a*b": a * b,
        }

        relations = []

        for output in output_values:

            if not isinstance(
                output,
                (int, float)
            ):
                relations.append("UNKNOWN")
                continue

            matches = [
                name
                for name, value in operations.items()
                if value == output
            ]

            if len(matches) == 1:
                relations.append(matches[0])

            elif len(matches) > 1:
                relations.append(
                    "=".join(matches)
                )

            else:
                relations.append("UNKNOWN")

        return tuple(relations)

    # =========================================================
    # ANALISAR UMA EXPRESSÃO
    # =========================================================

    def _analyze_expression(
        self,
        expression
    ):
        try:
            tree = ast.parse(
                expression,
                mode="eval"
            )
        except SyntaxError:
            return {
                "kind": "unknown",
                "relation": None
            }

        if not isinstance(
            tree.body,
            ast.Compare
        ):
            return {
                "kind": "unknown",
                "relation": None
            }

        compare = tree.body

        if len(compare.ops) != 1:
            return {
                "kind": "unknown",
                "relation": None
            }

        if not isinstance(
            compare.ops[0],
            ast.Eq
        ):
            return {
                "kind": "unknown",
                "relation": None
            }

        if len(compare.comparators) != 1:
            return {
                "kind": "unknown",
                "relation": None
            }

        left = compare.left
        right = compare.comparators[0]

        if not isinstance(
            left,
            ast.Call
        ):
            return {
                "kind": "unknown",
                "relation": None
            }

        function_name = None

        if isinstance(
            left.func,
            ast.Name
        ):
            function_name = left.func.id

        input_values = []

        for argument in left.args:
            value = self._literal_value(
                argument
            )

            input_values.append(value)

        output_values = []

        if isinstance(
            right,
            (ast.Tuple, ast.List)
        ):
            for element in right.elts:
                value = self._literal_value(
                    element
                )

                output_values.append(value)

        else:
            value = self._literal_value(
                right
            )

            output_values.append(value)

        relation = self._infer_relation(
            input_values,
            output_values
        )

        return {
            "kind": "function_relation",
            "function": function_name,
            "input_arity": len(input_values),
            "output_arity": len(output_values),
            "relation": relation
        }

    # =========================================================
    # PERFIL CONTEXTUAL
    # =========================================================

    def context_profile(self, tests):

        expressions = self._extract_tests(
            tests
        )

        relations = []

        for expression in expressions:

            analysis = self._analyze_expression(
                expression
            )

            relation = analysis.get(
                "relation"
            )

            if relation is not None:
                relations.append(relation)
            else:
                relations.append(
                    ("UNKNOWN",)
                )

        relations.sort()

        return relations

    # =========================================================
    # ASSINATURA CONTEXTUAL
    # =========================================================

    def context_signature(self, tests):

        profile = self.context_profile(
            tests
        )

        raw = repr(profile)

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    # =========================================================
    # EXPERIÊNCIAS
    # =========================================================

    def _experiences(self):

        return [
            node
            for node in self.graph.nodes.values()
            if node["type"] == "experience"
        ]

    # =========================================================
    # NORMALIZAR REGIÃO
    # =========================================================

    def _normalize_region(
        self,
        region
    ):
        if region is None:
            return {
                "region_index": None,
                "region_type": None,
            }

        if isinstance(region, dict):
            return {
                "region_index": region.get(
                    "region_index"
                ),
                "region_type": region.get(
                    "region_type"
                ),
            }

        if isinstance(region, (tuple, list)):
            if len(region) >= 2:
                return {
                    "region_index": region[0],
                    "region_type": region[1],
                }

        return {
            "region_index": None,
            "region_type": None,
        }

    # =========================================================
    # REGISTRAR MEMÓRIA
    # =========================================================

    def remember(
        self,
        tests,
        path,
        score=1.0,
        region_path=None
    ):
        signature = self.context_signature(
            tests
        )

        profile = self.context_profile(
            tests
        )

        path = list(path)

        if region_path is None:
            region_path = [
                {
                    "region_index": None,
                    "region_type": None,
                }
                for _ in path
            ]
        else:
            region_path = [
                self._normalize_region(region)
                for region in region_path
            ]

        # Mantém compatibilidade caso a lista
        # de regiões seja menor que a trajetória.
        while len(region_path) < len(path):
            region_path.append({
                "region_index": None,
                "region_type": None,
            })

        for node in self.graph.nodes.values():

            if node["type"] != "context_memory":
                continue

            data = node["data"]

            if (
                data.get("context_signature")
                == signature
                and data.get("path")
                == path
                and data.get("region_path")
                == region_path
            ):
                return False

        memory_id = (
            "context_memory_"
            f"{len(self.graph.nodes):04d}"
        )

        self.graph.add_node(
            memory_id,
            "context_memory",
            {
                "context_signature": signature,
                "context_profile": profile,
                "path": path,
                "region_path": region_path,
                "score": float(score)
            }
        )

        return True

    # =========================================================
    # RECUPERAR TRAJETÓRIAS
    # =========================================================

    def trajectories_for(self, tests):

        signature = self.context_signature(
            tests
        )

        results = []

        for node in self.graph.nodes.values():

            if node["type"] != "context_memory":
                continue

            data = node["data"]

            if (
                data.get("context_signature")
                != signature
            ):
                continue

            results.append({
                "memory_id": node["id"],
                "path": data.get(
                    "path",
                    []
                ),
                "region_path": data.get(
                    "region_path",
                    []
                ),
                "score": float(
                    data.get(
                        "score",
                        0.0
                    )
                )
            })

        results.sort(
            key=lambda item: (
                item["score"],
                -len(item["path"])
            ),
            reverse=True
        )

        return results

    # =========================================================
    # MELHOR TRAJETÓRIA
    # =========================================================

    def best_trajectory(self, tests):

        trajectories = self.trajectories_for(
            tests
        )

        if not trajectories:
            return None

        return trajectories[0]

    # =========================================================
    # PRIORIDADES
    # =========================================================

    def mutation_priorities(self, tests):

        trajectories = self.trajectories_for(
            tests
        )

        priorities = {}

        for trajectory in trajectories:

            path = trajectory["path"]
            score = trajectory["score"]

            for index, rule in enumerate(path):

                priority = (
                    (len(path) - index)
                    * score
                )

                priorities[rule] = (
                    priorities.get(
                        rule,
                        0
                    )
                    + priority
                )

        return dict(
            sorted(
                priorities.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
