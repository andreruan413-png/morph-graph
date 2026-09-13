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


def main():

    graph = Graph()

    initial_code = """
def calcular(a, b):
    return (a - b, a + b)
"""

    tests = """
TEST: assert calcular(2, 3)[0] == 5
TEST: assert calcular(2, 3)[1] == 6
"""

    graph.add_node(
        "program",
        "code",
        {
            "code": initial_code,
            "language": "python"
        }
    )

    mutator = AutomaticASTMutator()

    def evaluator(code):

        result = evaluate_problem(
            code,
            tests
        )

        return result.as_dict()

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3
    )

    result = search.search(
        "program"
    )

    print()
    print("=== PATH SEARCH ===")

    print(
        "Sucesso:",
        result["success"]
    )

    print(
        "Nós explorados:",
        result["explored"]
    )

    print(
        "Profundidade:",
        result["best"].get(
            "depth"
        )
    )

    print(
        "Score:",
        result["best"]["score"]
    )

    print()
    print("CAMINHO:")

    for step in result["path"]:
        print(
            " -> ",
            step,
            sep=""
        )

    final_node = graph.nodes[
        result["best"]["node_id"]
    ]

    print()
    print("CÓDIGO FINAL:")

    print(
        final_node["data"]["code"]
    )

    assert result["success"] is True

    assert result["best"]["score"] == 1.0

    assert result["best"]["depth"] == 2

    assert len(result["path"]) == 2

    assert (
        final_node["data"]["code"].strip()
        != initial_code.strip()
    )

    print()
    print("PATH SEARCH: OK")


if __name__ == "__main__":
    main()
