import ast
import copy


class ASTMutation(ast.NodeTransformer):

    def __init__(self, operation):
        super().__init__()
        self.operation = operation
        self.changed = False

    def visit_BinOp(self, node):
        self.generic_visit(node)

        if self.operation == "plus_to_minus":

            if isinstance(node.op, ast.Add):
                node.op = ast.Sub()
                self.changed = True

        elif self.operation == "swap_operands":

            if isinstance(node.op, ast.Add):
                node.left, node.right = (
                    node.right,
                    node.left
                )
                self.changed = True

        return node


class ASTMutationRule:

    def __init__(self, name, operation):
        self.name = name
        self.operation = operation

    def applies_to(self, node):
        return node["type"] == "code"

    def transform(self, graph, source_id, target_id):

        source = graph.nodes[source_id]

        if not self.applies_to(source):
            raise ValueError(
                f"Regra '{self.name}' não aplicável."
            )

        code = source["data"]["code"]

        tree = ast.parse(code)

        mutator = ASTMutation(
            self.operation
        )

        new_tree = mutator.visit(
            copy.deepcopy(tree)
        )

        if not mutator.changed:
            raise ValueError(
                f"Regra '{self.name}' não encontrou "
                "uma transformação possível."
            )

        ast.fix_missing_locations(new_tree)

        new_code = ast.unparse(new_tree)

        graph.add_node(
            target_id,
            "code",
            {
                "code": new_code,
                "language": "python",
                "generated_by": self.name,
                "source_node": source_id,
                "mutation_type": "AST",
                "operation": self.operation
            }
        )

        graph.connect(
            source_id,
            target_id,
            self.name
        )

        graph.history.append({
            "action": "ast_transform",
            "source": source_id,
            "rule": self.name,
            "target": target_id
        })

        return graph.nodes[target_id]
