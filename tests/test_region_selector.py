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
from engine.region_selector import RegionSelector


def main():

    graph = Graph()

    graph.add_node(
        "exp_add_mult",
        "experience",
        {
            "solution_node": "solution_add_mult",
            "score": 1.0,
            "generations": [
                {
                    "selected": {
                        "rule": "binop_0_sub_to_add"
                    }
                },
                {
                    "selected": {
                        "rule": "binop_1_add_to_mult"
                    }
                }
            ]
        }
    )

    graph.add_node(
        "solution_add_mult",
        "code",
        {
            "code": """
def calcular(a, b):
    return (a + b, a * b)
"""
        }
    )

    graph.add_node(
        "exp_swap",
        "experience",
        {
            "solution_node": "solution_swap",
            "score": 1.0,
            "generations": [
                {
                    "selected": {
                        "rule": "binop_0_swap"
                    }
                }
            ]
        }
    )

    graph.add_node(
        "solution_swap",
        "code",
        {
            "code": """
def inverter(a, b):
    return b - a
"""
        }
    )

    selector = RegionSelector(graph)

    result = selector.select(
        """
def novo(x, y):
    return (x - y, x + y)
"""
    )

    print()
    print("=== REGION SELECTOR ===")

    print(
        "Experiência selecionada:",
        result["selected"]["experience_id"]
    )

    print(
        "Similaridade:",
        result["selected"]["similarity"]
    )

    print(
        "Trajetória:",
        result["selected"]["path"]
    )

    print(
        "Prioridades:",
        result["priorities"]
    )

    assert result["selected"]["experience_id"] == (
        "exp_add_mult"
    )

    assert result["priorities"][
        "binop_0_sub_to_add"
    ] > 0

    print()
    print("REGION SELECTOR: OK")


if __name__ == "__main__":
    main()
