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
from engine.transition_memory import (
    TransitionMemory
)


def main():

    graph = Graph()

    source_code = """
def resolver(a, b):
    return a - b
"""

    target_code = """
def resolver(a, b):
    return a + b
"""

    graph.add_node(
        "source",
        "code",
        {
            "code": source_code,
            "language": "python"
        }
    )

    graph.add_node(
        "target",
        "code",
        {
            "code": target_code,
            "language": "python",
            "source_node": "source",
            "generated_by":
                "binop_0_sub_to_add"
        }
    )

    graph.connect(
        "source",
        "target",
        "binop_0_sub_to_add"
    )

    graph.add_node(
        "evaluation",
        "evaluation",
        {
            "target_node": "target",
            "success": True,
            "score": 1.0
        }
    )

    graph.connect(
        "target",
        "evaluation",
        "evaluated_by"
    )

    memory = TransitionMemory(
        graph
    )

    transitions = memory.next_transitions(
        source_code
    )

    print()
    print("=== TRANSITION MEMORY ===")
    print(
        "Transições encontradas:",
        len(transitions)
    )

    for transition in transitions:
        print(
            "Mutação:",
            transition["mutation"]
        )
        print(
            "Sucesso:",
            transition["success"]
        )

    priorities = memory.mutation_priority(
        source_code
    )

    print(
        "Prioridades:",
        priorities
    )

    next_step = memory.learned_next_step(
        source_code
    )

    print(
        "Próximo passo aprendido:",
        next_step
    )

    assert len(transitions) == 1

    assert (
        transitions[0]["mutation"]
        == "binop_0_sub_to_add"
    )

    assert (
        transitions[0]["success"]
        is True
    )

    assert (
        next_step
        == "binop_0_sub_to_add"
    )

    print()
    print(
        "TRANSITION MEMORY: OK"
    )


if __name__ == "__main__":
    main()
