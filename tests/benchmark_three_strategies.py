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
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch


SOURCE = """
def calcular(a, b):
    return (a - b, a + b)
"""

TESTS = """
TEST: assert calcular(2, 3)[0] == 5
TEST: assert calcular(2, 3)[1] == 6
"""


def evaluator(code):
    return evaluate_problem(
        code,
        TESTS
    ).as_dict()


def make_graph():
    graph = Graph()

    graph.add_node(
        "problem",
        "problem",
        {
            "description": "problema de teste"
        }
    )

    graph.add_node(
        "source",
        "code",
        {
            "code": SOURCE,
            "language": "python"
        }
    )

    graph.add_node(
        "tests",
        "tests",
        {
            "content": TESTS
        }
    )

    graph.connect(
        "problem",
        "source",
        "has_source"
    )

    graph.connect(
        "problem",
        "tests",
        "has_tests"
    )

    return graph


def add_training_experience(graph):

    graph.add_node(
        "training_solution",
        "code",
        {
            "code": """
def treinamento(x, y):
    return (x + y, x * y)
""",
            "language": "python"
        }
    )

    graph.add_node(
        "training_experience",
        "experience",
        {
            "solution_node": "training_solution",
            "score": 1.0,
            "problem_id": "training_problem",

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


def run(
    label,
    use_trajectory,
    use_structure,
    training=False
):

    graph = make_graph()

    if training:
        add_training_experience(graph)

    mutator = AutomaticASTMutator()

    search = PathSearch(
        graph,
        mutator,
        evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=use_trajectory,
        use_structure=use_structure
    )

    result = search.search("source")

    print(
        f"{label}: "
        f"sucesso={result['success']} "
        f"explorados={result['explored']} "
        f"profundidade={result['best'].get('depth', 0)}"
    )

    return result


def main():

    print()
    print("=== BENCHMARK: 3 ESTRATÉGIAS ===")
    print()

    print("FASE 1: SEM APRENDIZADO")
    print()

    baseline = run(
        "1. BUSCA CEGA",
        False,
        False,
        False
    )

    print()
    print("FASE 2: COM EXPERIÊNCIA PRÉVIA")
    print()

    trajectory = run(
        "2. TRAJETÓRIA",
        True,
        False,
        True
    )

    combined = run(
        "3. ESTRUTURA + TRAJETÓRIA",
        True,
        True,
        True
    )

    print()
    print("=== RESULTADO ===")

    print(
        "Busca cega:",
        baseline["explored"]
    )

    print(
        "Trajetória:",
        trajectory["explored"]
    )

    print(
        "Estrutura + trajetória:",
        combined["explored"]
    )

    print()

    if combined["success"]:

        print(
            "CAMINHO APRENDIDO:"
        )

        for rule in combined["path"]:
            print(
                " ->",
                rule
            )

    print()
    print("BENCHMARK: OK")


if __name__ == "__main__":
    main()
