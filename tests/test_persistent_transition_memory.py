import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.path_search import PathSearch
from engine.transition_memory import TransitionMemory


MEMORY_FILE = "transition_memory.json"


def evaluator(code):

    namespace = {}

    try:

        exec(code, namespace)

        fn = namespace.get("resolver")

        if fn is None:
            return {
                "success": False,
                "score": 0.0,
                "reason": "resolver não encontrada"
            }

        result = fn(2, 3)

        if result == (5, 6):
            return {
                "success": True,
                "score": 1.0,
                "reason": "resultado correto"
            }

        return {
            "success": False,
            "score": 0.0,
            "reason": f"resultado incorreto: {result}"
        }

    except Exception as exc:

        return {
            "success": False,
            "score": 0.0,
            "reason": f"erro: {exc}"
        }


def add_source(graph, node_id, code):

    graph.add_node(
        node_id,
        "code",
        {
            "code": code,
            "language": "python",
            "role": "source"
        }
    )


def train():

    graph = Graph()

    code = """def resolver(a, b):
    return (a - b, a + b)
"""

    add_source(
        graph,
        "training_source",
        code
    )

    search = PathSearch(
        graph,
        AutomaticASTMutator(),
        evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=True,
        use_structure=True,
        use_pruner=False
    )

    result = search.search(
        "training_source"
    )

    if not result["success"]:
        raise RuntimeError(
            "Treinamento não encontrou solução."
        )

    memory = TransitionMemory(graph)

    memory.record_trajectory(
        code,
        result["path"]
    )

    memory.record_search_result(
        "training_source",
        result["path"]
    )

    exported = memory.export(
        MEMORY_FILE
    )

    print("=== TREINAMENTO ===")
    print(
        "Sucesso:",
        result["success"]
    )
    print(
        "Caminho:",
        result["path"]
    )
    print(
        "Memória exportada:",
        exported
    )

    return result["path"]


def test_first_step():

    graph = Graph()

    code = """def calcular(x, y):
    return (x - y, x + y)
"""

    add_source(
        graph,
        "new_source",
        code
    )

    memory = TransitionMemory(graph)

    memory.load(
        MEMORY_FILE
    )

    priorities = memory.mutation_priority(
        code
    )

    learned = memory.learned_next_step(
        code
    )

    print()
    print("=== NOVO GRAFO / ESTADO A ===")
    print(
        "Prioridades:",
        priorities
    )
    print(
        "Próximo passo:",
        learned
    )

    if learned != "binop_1_add_to_mult":
        raise RuntimeError(
            "Primeiro passo aprendido incorretamente: "
            + str(learned)
        )

    print(
        "PRIMEIRA TRANSIÇÃO: OK"
    )


def test_second_step():

    graph = Graph()

    initial_code = """def calcular(x, y):
    return (x - y, x + y)
"""

    intermediate_code = """def calcular(x, y):
    return (x - y, x * y)
"""

    add_source(
        graph,
        "state_a",
        initial_code
    )

    add_source(
        graph,
        "state_b",
        intermediate_code
    )

    memory = TransitionMemory(graph)

    memory.load(
        MEMORY_FILE
    )

    priorities = memory.mutation_priority(
        intermediate_code
    )

    learned = memory.learned_next_step(
        intermediate_code
    )

    print()
    print("=== NOVO GRAFO / ESTADO B ===")
    print(
        "Prioridades:",
        priorities
    )
    print(
        "Próximo passo:",
        learned
    )

    if learned != "binop_0_sub_to_add":
        raise RuntimeError(
            "Segundo passo aprendido incorretamente: "
            + str(learned)
        )

    print(
        "SEGUNDA TRANSIÇÃO: OK"
    )


def main():

    train()

    test_first_step()

    test_second_step()

    print()
    print(
        "FULL TRAJECTORY MEMORY: OK"
    )


if __name__ == "__main__":
    main()
