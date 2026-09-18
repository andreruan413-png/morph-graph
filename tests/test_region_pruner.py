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
from engine.region_pruner import RegionPruner


class Candidate:

    def __init__(self, name):
        self.name = name


def main():

    graph = Graph()

    graph.add_node(
        "solution",
        "code",
        {
            "code": """
def calcular(a, b):
    return (a + b, a * b)
"""
        }
    )

    graph.add_node(
        "experience",
        "experience",
        {
            "solution_node": "solution",
            "score": 1.0,
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

    candidates = [
        Candidate("binop_0_sub_to_add"),
        Candidate("binop_0_swap"),
        Candidate("binop_0_add_to_sub"),
        Candidate("binop_0_mult_to_add")
    ]

    pruner = RegionPruner(
        graph,
        exploration_rate=0.25
    )

    result = pruner.filter(
        """
def novo(x, y):
    return (x - y, x + y)
""",
        candidates
    )

    names = [
        candidate.name
        for candidate in result
    ]

    print()
    print("=== REGION PRUNER ===")
    print("Candidatos recebidos:", len(candidates))
    print("Candidatos após gating:", len(result))
    print("Candidatos:", names)

    assert (
        "binop_0_sub_to_add"
        in names
    )

    assert len(result) < len(candidates)

    print()
    print("REGION PRUNER: OK")


if __name__ == "__main__":
    main()
