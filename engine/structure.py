import ast


def structural_profile(code):
    tree = ast.parse(code)

    profile = {
        "functions": 0,
        "classes": 0,
        "binops": 0,
        "add": 0,
        "sub": 0,
        "mult": 0,
        "div": 0,
        "comparisons": 0,
        "eq": 0,
        "neq": 0,
        "lt": 0,
        "lte": 0,
        "gt": 0,
        "gte": 0,
        "boolops": 0,
        "and": 0,
        "or": 0,
        "constants": 0,
        "asserts": 0,
        "returns": 0,
        "arguments": 0,
    }

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            profile["functions"] += 1
            profile["arguments"] += len(
                node.args.args
            )

        elif isinstance(node, ast.ClassDef):
            profile["classes"] += 1

        elif isinstance(node, ast.BinOp):
            profile["binops"] += 1

            if isinstance(node.op, ast.Add):
                profile["add"] += 1

            elif isinstance(node.op, ast.Sub):
                profile["sub"] += 1

            elif isinstance(node.op, ast.Mult):
                profile["mult"] += 1

            elif isinstance(node.op, ast.Div):
                profile["div"] += 1

        elif isinstance(node, ast.Compare):
            profile["comparisons"] += len(
                node.ops
            )

            for op in node.ops:

                if isinstance(op, ast.Eq):
                    profile["eq"] += 1

                elif isinstance(op, ast.NotEq):
                    profile["neq"] += 1

                elif isinstance(op, ast.Lt):
                    profile["lt"] += 1

                elif isinstance(op, ast.LtE):
                    profile["lte"] += 1

                elif isinstance(op, ast.Gt):
                    profile["gt"] += 1

                elif isinstance(op, ast.GtE):
                    profile["gte"] += 1

        elif isinstance(node, ast.BoolOp):
            profile["boolops"] += 1

            if isinstance(node.op, ast.And):
                profile["and"] += 1

            elif isinstance(node.op, ast.Or):
                profile["or"] += 1

        elif isinstance(node, ast.Constant):

            if isinstance(
                node.value,
                (int, float)
            ) and not isinstance(
                node.value,
                bool
            ):
                profile["constants"] += 1

        elif isinstance(node, ast.Assert):
            profile["asserts"] += 1

        elif isinstance(node, ast.Return):
            profile["returns"] += 1

    return profile


def structural_similarity(
    profile_a,
    profile_b
):

    keys = profile_a.keys()

    total = len(keys)

    if total == 0:
        return 0.0

    matches = 0

    for key in keys:

        if profile_a.get(key, 0) == profile_b.get(
            key,
            0
        ):
            matches += 1

    return matches / total
