import ast
from dataclasses import dataclass


@dataclass
class CompositeMutation:
    name: str
    _code: str
    operations: list

    def code(self):
        return self._code

    def as_dict(self):
        return {
            "name": self.name,
            "code": self._code,
            "operations": self.operations,
        }


def _make_binop(left, op, right):
    return ast.BinOp(
        left=left,
        op=op(),
        right=right
    )


def compose_add_swap(code):
    """
    Transformação composta:

        A + B -> B - A

    Conceitualmente combina:

        add_to_sub
        +
        swap_operands
    """

    tree = ast.parse(code)

    class Transformer(ast.NodeTransformer):
        changed = False

        def visit_BinOp(self, node):
            self.generic_visit(node)

            if self.changed:
                return node

            if not isinstance(node.op, ast.Add):
                return node

            left = node.left
            right = node.right

            new_node = _make_binop(
                right,
                ast.Sub,
                left
            )

            self.changed = True

            return ast.copy_location(new_node, node)

    transformer = Transformer()
    new_tree = transformer.visit(tree)

    if not transformer.changed:
        return None

    ast.fix_missing_locations(new_tree)

    return ast.unparse(new_tree)


def generate_composite_mutations(code):
    candidates = []

    new_code = compose_add_swap(code)

    if new_code and new_code != code:
        candidates.append(
            CompositeMutation(
                name="composite_add_to_sub_swap",
                _code=new_code,
                operations=[
                    "add_to_sub",
                    "swap_operands",
                ],
            )
        )

    return candidates


if __name__ == "__main__":
    source = """def resolver(a, b):
    return (a + b, a - b)
"""

    for candidate in generate_composite_mutations(source):
        print("REGRA:", candidate.name)
        print("OPERAÇÕES:", candidate.operations)
        print(candidate.code())
