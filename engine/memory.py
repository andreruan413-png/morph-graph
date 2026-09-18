import ast
import hashlib


class _NormalizeAST(ast.NodeTransformer):

    def __init__(self):
        super().__init__()
        self.variable_map = {}
        self.argument_index = 0

    def _normalize_name(self, name):
        if name not in self.variable_map:
            self.variable_map[name] = f"VAR{len(self.variable_map)}"
        return self.variable_map[name]

    def visit_Name(self, node):
        node.id = self._normalize_name(node.id)
        return node

    def visit_arg(self, node):
        node.arg = self._normalize_name(node.arg)
        return node

    def visit_FunctionDef(self, node):
        node.name = "FUNCTION"
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        node.name = "FUNCTION"
        self.generic_visit(node)
        return node


def normalized_ast(code):
    tree = ast.parse(code)

    normalizer = _NormalizeAST()
    tree = normalizer.visit(tree)

    ast.fix_missing_locations(tree)

    return tree


def code_signature(code):
    tree = normalized_ast(code)

    normalized = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


class GraphMemory:

    def __init__(self, graph):
        self.graph = graph

    def signatures(self):
        return {
            code_signature(
                node["data"].get("code", "")
            )
            for node in self.graph.nodes.values()
            if node["type"] == "code"
            and node["data"].get("code")
        }

    def has_seen(self, code):
        return code_signature(code) in self.signatures()

    def remember(self, node_id):
        node = self.graph.nodes.get(node_id)

        if not node or node["type"] != "code":
            return False

        node["data"]["memory_signature"] = code_signature(
            node["data"].get("code", "")
        )

        return True

    def is_duplicate(self, node_id):
        node = self.graph.nodes.get(node_id)

        if not node:
            return False

        code = node["data"].get("code", "")

        if not code:
            return False

        signature = code_signature(code)

        matches = []

        for other_id, other in self.graph.nodes.items():

            if other_id == node_id:
                continue

            if other["type"] != "code":
                continue

            other_code = other["data"].get("code", "")

            if not other_code:
                continue

            if code_signature(other_code) == signature:
                matches.append(other_id)

        return bool(matches)
