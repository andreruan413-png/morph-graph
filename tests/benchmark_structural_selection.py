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
def resolver(x, y):
    return (x - y, x + y)
"""

TESTS = """
TEST: assert resolver(2, 3)[0] == 5
TEST: assert resolver(2, 3)[1] == 6
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
            "description":
                "problema novo"
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


def add_experience(
    graph,
    experience_id,
    solution_id,
    code,
    path
):

    graph.add_node(
        solution_id,
        "code",
        {
            "code": code,
            "language": "python"
        }
    )

    graph.add_node(
        experience_id,
        "experience",
        {
            "solution_node": solution_id,
            "score": 1.0,
            "problem_id":
                f"{experience_id}_problem",

            "generations": [
                {
                    "selected": {
                        "rule": rule
                    }
                }
                for rule in path
            ]
        }
    )


def add_training_memory(graph):

    # EXPERIÊNCIA A
    #
    # Estruturalmente semelhante ao
    # problema que vamos resolver.

    add_experience(
        graph,
        "experience_A",
        "solution_A",
        """
def treinamento_a(a, b):
    return (a + b, a * b)
""",
        [
            "binop_0_sub_to_add",
            "binop_1_add_to_mult"
        ]
    )

    # EXPERIÊNCIA B
    #
    # Caminho diferente.

    add_experience(
        graph,
        "experience_B",
        "solution_B",
        """
def treinamento_b(a, b):
    return b - a
""",
        [
            "binop_0_swap"
        ]
    )

    # EXPERIÊNCIA C
    #
    # Outra estratégia.

    add_experience(
        graph,
        "experience_C",
        "solution_C",
        """
def treinamento_c(a, b):
    return a - b
""",
        [
            "binop_0_add_to_sub"
        ]
    )

    # EXPERIÊNCIA D
    #
    # Outra estrutura.

    add_experience(
        graph,
        "experience_D",
        "solution_D",
        """
def treinamento_d(a, b, c):
    return a + b + c
""",
        [
            "binop_0_mult_to_add"
        ]
    )


def run(
    label,
    use_trajectory,
    use_structure,
    training
):

    graph = make_graph()

    if training:
        add_training_memory(graph)

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

    result = search.search(
        "source"
    )

    print(
        f"{label}: "
        f"sucesso={result['success']} "
        f"explorados={result['explored']} "
        f"profundidade="
        f"{result['best'].get('depth', 0)}"
    )

    if result.get("region"):

        selected = result[
            "region"
        ].get("selected")

        if selected:

            print(
                "  experiência selecionada:",
                selected["experience_id"]
            )

            print(
                "  similaridade:",
                selected["similarity"]
            )

            print(
                "  trajetória:",
                selected["path"]
            )

    return result


def main():

    print()
    print(
        "=== SELEÇÃO ESTRUTURAL ==="
    )
    print()

    baseline = run(
        "1. BUSCA CEGA",
        False,
        False,
        False
    )

    trajectory = run(
        "2. TRAJETÓRIA GLOBAL",
        True,
        False,
        True
    )

    structural = run(
        "3. ESTRUTURA + TRAJETÓRIA",
        True,
        True,
        True
    )

    print()
    print(
        "=== COMPARAÇÃO ==="
    )

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
        structural["explored"]
    )

    print()

    if structural["success"]:

        print(
            "CAMINHO ENCONTRADO:"
        )

        for rule in structural["path"]:
            print(
                " ->",
                rule
            )

    print()
    print(
        "SELEÇÃO ESTRUTURAL: OK"
    )


if __name__ == "__main__":
    main()
