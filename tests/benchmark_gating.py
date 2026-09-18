import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.path_search import PathSearch


TRAINING_CODE = """
def treinamento(a, b):
    return (a + b, a * b)
"""


def evaluator_factory(expected_name):

    def evaluate(code):

        namespace = {}

        try:
            exec(
                code,
                namespace
            )

            fn = namespace[expected_name]

            result = fn(2, 3)

            if result == (5, 6):
                return {
                    "success": True,
                    "score": 1.0,
                    "reason": "solução correta"
                }

            return {
                "success": False,
                "score": 0.0,
                "reason": "resultado incorreto"
            }

        except Exception as exc:

            return {
                "success": False,
                "score": 0.0,
                "reason": str(exc)
            }

    return evaluate


PROBLEMS = [
    "resolver_a",
    "resolver_b",
    "resolver_c",
    "resolver_d",
    "resolver_e",
    "resolver_f",
    "resolver_g",
    "resolver_h",
    "resolver_i",
    "resolver_j"
]


def source_code(name):

    return f"""
def {name}(x, y):
    return (x - y, x + y)
"""


def train_graph():

    graph = Graph()

    graph.add_node(
        "training_solution",
        "code",
        {
            "code": TRAINING_CODE,
            "language": "python"
        }
    )

    graph.add_node(
        "training_experience",
        "experience",
        {
            "solution_node":
                "training_solution",
            "score":
                1.0,
            "generations": [
                {
                    "selected": {
                        "rule":
                            "binop_0_sub_to_add"
                    }
                },
                {
                    "selected": {
                        "rule":
                            "binop_1_add_to_mult"
                    }
                }
            ]
        }
    )

    # Experiências deliberadamente diferentes.
    graph.add_node(
        "noise_solution",
        "code",
        {
            "code": """
def outra(a, b):
    return b - a
"""
        }
    )

    graph.add_node(
        "noise_experience",
        "experience",
        {
            "solution_node":
                "noise_solution",
            "score":
                1.0,
            "generations": [
                {
                    "selected": {
                        "rule":
                            "binop_0_swap"
                    }
                }
            ]
        }
    )

    return graph


def run_case(
    graph,
    name,
    use_trajectory,
    use_structure,
    use_pruner
):

    graph.add_node(
        f"{name}_source",
        "code",
        {
            "code":
                source_code(name),
            "language":
                "python"
        }
    )

    source_id = f"{name}_source"

    mutator = AutomaticASTMutator()

    evaluator = evaluator_factory(name)

    search = PathSearch(
        graph,
        mutator,
        evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=use_trajectory,
        use_structure=use_structure,
        use_pruner=use_pruner
    )

    return search.search(source_id)


def benchmark(
    learned,
    structure,
    pruner
):

    graph = train_graph()

    solved = 0
    explored = 0
    generated = 0
    evaluated = 0
    discarded = 0
    depths = []

    for name in PROBLEMS:

        result = run_case(
            graph,
            name,
            learned,
            structure,
            pruner
        )

        if result["success"]:
            solved += 1

        explored += result.get(
            "explored",
            0
        )

        generated += result.get(
            "generated_candidates",
            0
        )

        evaluated += result.get(
            "evaluated_candidates",
            0
        )

        discarded += result.get(
            "discarded_candidates",
            0
        )

        depths.append(
            result.get(
                "best",
                {}
            ).get(
                "depth",
                0
            )
        )

    return {
        "solved": solved,
        "explored": explored,
        "generated": generated,
        "evaluated": evaluated,
        "discarded": discarded,
        "avg_depth":
            sum(depths) / len(depths)
    }


def main():

    print()
    print("================================")
    print(" BENCHMARK: GATING APRENDIDO")
    print("================================")

    print()
    print("10 problemas novos")
    print()

    baseline = benchmark(
        False,
        False,
        False
    )

    trajectory = benchmark(
        True,
        False,
        False
    )

    structural = benchmark(
        True,
        True,
        False
    )

    gating = benchmark(
        True,
        True,
        True
    )

    results = [
        (
            "BUSCA CEGA",
            baseline
        ),
        (
            "TRAJETÓRIA",
            trajectory
        ),
        (
            "ESTRUTURA + TRAJETÓRIA",
            structural
        ),
        (
            "ESTRUTURA + TRAJETÓRIA + GATING",
            gating
        )
    ]

    print(
        f"{'ESTRATÉGIA':<32}"
        f"{'SOLUÇÕES':>10}"
        f"{'NÓS':>10}"
        f"{'GERADOS':>10}"
        f"{'AVALIADOS':>12}"
        f"{'DESCARTADOS':>13}"
    )

    print("-" * 87)

    for label, data in results:

        print(
            f"{label:<32}"
            f"{data['solved']:>7}/10"
            f"{data['explored']:>10}"
            f"{data['generated']:>10}"
            f"{data['evaluated']:>12}"
            f"{data['discarded']:>13}"
        )

    print()

    base_eval = baseline["evaluated"]
    gate_eval = gating["evaluated"]

    if base_eval:
        reduction = (
            1 -
            gate_eval / base_eval
        ) * 100
    else:
        reduction = 0

    print(
        f"Redução de avaliações com gating: "
        f"{reduction:.2f}%"
    )

    print(
        f"Profundidade média com gating: "
        f"{gating['avg_depth']:.2f}"
    )

    print()

    if gating["solved"] < 10:

        print(
            "ATENÇÃO: gating perdeu soluções."
        )

        print(
            "O mecanismo precisa aumentar "
            "a exploração."
        )

        return

    print(
        "GATING: TODAS AS SOLUÇÕES PRESERVADAS"
    )


if __name__ == "__main__":
    main()
