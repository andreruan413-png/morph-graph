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
from engine.trajectory_guidance import TrajectoryGuidance


def main():

    graph = Graph()

    graph.add_node(
        "solution_001",
        "code",
        {"code": "def x(): pass"}
    )

    graph.add_node(
        "experience_001",
        "experience",
        {
            "problem_id": "problem_001",
            "solution_node": "solution_001",
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

    guidance = TrajectoryGuidance(graph)

    first = guidance.priorities([])

    second = guidance.priorities(
        ["binop_0_sub_to_add"]
    )

    print()
    print("=== TRAJECTORY GUIDANCE ===")
    print("Primeiro passo:", first)
    print("Segundo passo:", second)

    assert first["binop_0_sub_to_add"] == 1
    assert second["binop_1_add_to_mult"] == 1

    print()
    print("TRAJECTORY GUIDANCE: OK")


if __name__ == "__main__":
    main()
