import ast
import copy

from engine.composite_mutation import generate_composite_mutations


class MutationCandidate:
    def __init__(
        self,
        name,
        tree,
        region_index=None,
        region_type=None,
        mutation_type=None,
    ):
        self.name = name
        self.tree = tree
        self.region_index = region_index
        self.region_type = region_type
        self.mutation_type = mutation_type

    def code(self):
        ast.fix_missing_locations(self.tree)
        return ast.unparse(self.tree)

    def as_dict(self):
        return {
            "name": self.name,
            "region_index": self.region_index,
            "region_type": self.region_type,
            "mutation_type": self.mutation_type,
            "code": self.code(),
        }


class AutomaticASTMutator:

    def _find_nodes(self, tree, node_type):
        return [
            node
            for node in ast.walk(tree)
            if isinstance(node, node_type)
        ]

    def _replace_binop(
        self,
        tree,
        target_index,
        new_op,
        name,
    ):
        new_tree = copy.deepcopy(tree)

        count = 0

        for node in ast.walk(new_tree):
            if isinstance(node, ast.BinOp):

                if count == target_index:
                    node.op = new_op
                    break

                count += 1

        return MutationCandidate(
            name=name,
            tree=new_tree,
            region_index=target_index,
            region_type="BinOp",
            mutation_type="operator_change",
        )

    def _swap_operands(
        self,
        tree,
        target_index,
        name,
    ):
        new_tree = copy.deepcopy(tree)

        count = 0

        for node in ast.walk(new_tree):
            if isinstance(node, ast.BinOp):

                if count == target_index:
                    node.left, node.right = (
                        node.right,
                        node.left,
                    )
                    break

                count += 1

        return MutationCandidate(
            name=name,
            tree=new_tree,
            region_index=target_index,
            region_type="BinOp",
            mutation_type="operand_swap",
        )

    def generate(self, code):
        original = ast.parse(code)

        candidates = []

        operators = {
            ast.Add: [
                (ast.Sub, "add_to_sub"),
                (ast.Mult, "add_to_mult"),
            ],
            ast.Sub: [
                (ast.Add, "sub_to_add"),
                (ast.Mult, "sub_to_mult"),
            ],
            ast.Mult: [
                (ast.Add, "mult_to_add"),
                (ast.Sub, "mult_to_sub"),
            ],
        }

        binops = self._find_nodes(
            original,
            ast.BinOp,
        )

        for index, node in enumerate(binops):

            node_type = type(node.op)

            for new_op, operation_name in operators.get(
                node_type,
                [],
            ):
                candidates.append(
                    self._replace_binop(
                        original,
                        index,
                        new_op(),
                        f"binop_{index}_{operation_name}",
                    )
                )

            if node_type in (
                ast.Add,
                ast.Sub,
                ast.Mult,
            ):
                candidates.append(
                    self._swap_operands(
                        original,
                        index,
                        f"binop_{index}_swap",
                    )
                )

        composite_candidates = (
            generate_composite_mutations(code)
        )

        for candidate in composite_candidates:
            candidate.region_index = None
            candidate.region_type = "BinOp"

            if not getattr(
                candidate,
                "mutation_type",
                None,
            ):
                candidate.mutation_type = "composite"

        candidates.extend(
            composite_candidates
        )

        return candidates
