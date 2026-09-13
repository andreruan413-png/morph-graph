import ast
import copy


class MutationCandidate:

    def __init__(self, name, tree):
        self.name = name
        self.tree = tree

    def code(self):
        ast.fix_missing_locations(self.tree)
        return ast.unparse(self.tree)


class AutomaticASTMutator:

    def generate(self, code):

        original = ast.parse(code)

        candidates = []

        # ==================================================
        # BINOP
        # ==================================================

        for index, node in enumerate(
            self._find_nodes(original, ast.BinOp)
        ):

            if isinstance(node.op, ast.Add):

                candidates.append(
                    self._replace_binop(
                        original,
                        index,
                        ast.Sub(),
                        f"binop_{index}_add_to_sub"
                    )
                )

                candidates.append(
                    self._swap_operands(
                        original,
                        index,
                        f"binop_{index}_swap"
                    )
                )

                candidates.append(
                    self._replace_binop(
                        original,
                        index,
                        ast.Mult(),
                        f"binop_{index}_add_to_mult"
                    )
                )

            elif isinstance(node.op, ast.Sub):

                candidates.append(
                    self._replace_binop(
                        original,
                        index,
                        ast.Add(),
                        f"binop_{index}_sub_to_add"
                    )
                )

                candidates.append(
                    self._swap_operands(
                        original,
                        index,
                        f"binop_{index}_swap"
                    )
                )

            elif isinstance(node.op, ast.Mult):

                candidates.append(
                    self._replace_binop(
                        original,
                        index,
                        ast.Div(),
                        f"binop_{index}_mult_to_div"
                    )
                )

            elif isinstance(node.op, ast.Div):

                candidates.append(
                    self._replace_binop(
                        original,
                        index,
                        ast.Mult(),
                        f"binop_{index}_div_to_mult"
                    )
                )

        # ==================================================
        # COMPARAÇÕES
        # ==================================================

        for index, node in enumerate(
            self._find_nodes(original, ast.Compare)
        ):

            for op_index, operator in enumerate(
                node.ops
            ):

                replacements = []

                if isinstance(operator, ast.Eq):

                    replacements = [
                        (
                            ast.NotEq(),
                            "eq_to_neq"
                        )
                    ]

                elif isinstance(operator, ast.NotEq):

                    replacements = [
                        (
                            ast.Eq(),
                            "neq_to_eq"
                        )
                    ]

                elif isinstance(operator, ast.Lt):

                    replacements = [
                        (
                            ast.LtE(),
                            "lt_to_lte"
                        ),
                        (
                            ast.Gt(),
                            "lt_to_gt"
                        )
                    ]

                elif isinstance(operator, ast.LtE):

                    replacements = [
                        (
                            ast.Lt(),
                            "lte_to_lt"
                        )
                    ]

                elif isinstance(operator, ast.Gt):

                    replacements = [
                        (
                            ast.GtE(),
                            "gt_to_gte"
                        ),
                        (
                            ast.Lt(),
                            "gt_to_lt"
                        )
                    ]

                elif isinstance(operator, ast.GtE):

                    replacements = [
                        (
                            ast.Gt(),
                            "gte_to_gt"
                        )
                    ]

                for replacement, name in replacements:

                    tree = copy.deepcopy(
                        original
                    )

                    compares = self._find_nodes(
                        tree,
                        ast.Compare
                    )

                    target = compares[index]

                    target.ops[op_index] = replacement

                    candidates.append(
                        MutationCandidate(
                            f"compare_{index}_{op_index}_{name}",
                            tree
                        )
                    )

        # ==================================================
        # CONSTANTES NUMÉRICAS
        # ==================================================

        for index, node in enumerate(
            self._numeric_constants(original)
        ):

            for delta, name in [
                (1, "plus_one"),
                (-1, "minus_one")
            ]:

                tree = copy.deepcopy(
                    original
                )

                constants = self._numeric_constants(
                    tree
                )

                target = constants[index]

                target.value = node.value + delta

                candidates.append(
                    MutationCandidate(
                        f"constant_{index}_{name}",
                        tree
                    )
                )

        # ==================================================
        # AND / OR
        # ==================================================

        for index, node in enumerate(
            self._find_nodes(original, ast.BoolOp)
        ):

            if isinstance(node.op, ast.And):

                tree = copy.deepcopy(
                    original
                )

                boolops = self._find_nodes(
                    tree,
                    ast.BoolOp
                )

                boolops[index].op = ast.Or()

                candidates.append(
                    MutationCandidate(
                        f"boolop_{index}_and_to_or",
                        tree
                    )
                )

            elif isinstance(node.op, ast.Or):

                tree = copy.deepcopy(
                    original
                )

                boolops = self._find_nodes(
                    tree,
                    ast.BoolOp
                )

                boolops[index].op = ast.And()

                candidates.append(
                    MutationCandidate(
                        f"boolop_{index}_or_to_and",
                        tree
                    )
                )

        return self._remove_duplicates(
            candidates
        )

    # ======================================================
    # BUSCA NÓS DA AST
    # ======================================================

    def _find_nodes(
        self,
        tree,
        node_type
    ):

        return [
            node
            for node in ast.walk(tree)
            if isinstance(node, node_type)
        ]

    # ======================================================
    # CONSTANTES NUMÉRICAS
    # ======================================================

    def _numeric_constants(
        self,
        tree
    ):

        return [
            node
            for node in ast.walk(tree)
            if (
                isinstance(node, ast.Constant)
                and isinstance(
                    node.value,
                    (int, float)
                )
                and not isinstance(
                    node.value,
                    bool
                )
            )
        ]

    # ======================================================
    # SUBSTITUIR BINOP
    # ======================================================

    def _replace_binop(
        self,
        original,
        index,
        operator,
        name
    ):

        tree = copy.deepcopy(
            original
        )

        binops = self._find_nodes(
            tree,
            ast.BinOp
        )

        if index >= len(binops):

            raise RuntimeError(
                "Índice de BinOp inválido: "
                f"{index} >= {len(binops)}"
            )

        target = binops[index]

        target.op = operator

        return MutationCandidate(
            name,
            tree
        )

    # ======================================================
    # TROCAR OPERANDOS
    # ======================================================

    def _swap_operands(
        self,
        original,
        index,
        name
    ):

        tree = copy.deepcopy(
            original
        )

        binops = self._find_nodes(
            tree,
            ast.BinOp
        )

        if index >= len(binops):

            raise RuntimeError(
                "Índice de BinOp inválido: "
                f"{index} >= {len(binops)}"
            )

        target = binops[index]

        target.left, target.right = (
            target.right,
            target.left
        )

        return MutationCandidate(
            name,
            tree
        )

    # ======================================================
    # REMOVER DUPLICATAS
    # ======================================================

    def _remove_duplicates(
        self,
        candidates
    ):

        seen = set()

        unique = []

        for candidate in candidates:

            try:

                generated_code = (
                    candidate.code()
                )

            except Exception:

                continue

            if generated_code in seen:
                continue

            seen.add(
                generated_code
            )

            unique.append(
                candidate
            )

        return unique
