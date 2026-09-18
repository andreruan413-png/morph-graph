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


def evaluator(code):
    namespace = {}

    try:
        exec(code, namespace)

        fn = namespace.get("resolver")

        if fn is None:
            return {
                "success": False,
                "score": 0.0,
                "reason": "função resolver não encontrada"
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
            "reason": str(exc)
        }


def add_source(graph, node_id, code):
    graph.add_node(
        node_id,
        "code",
        {
            "code": code,
            "language": "python"
        }
    )


def train_transition_memory(graph):
    source = """def resolver(a, b):
    return (a - b, a + b)
"""

    add_source(
        graph,
        "training_source",
        source
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

    return result


def run_problem(use_memory, index):
    graph = Graph()

    source = f"""def resolver(a, b):
    return (a - b, a + b)
"""

    add_source(
        graph,
        f"problem_{index}",
        source
    )

    if use_memory:
        train_transition_memory(graph)

    search = PathSearch(
        graph,
        AutomaticASTMutator(),
        evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=use_memory,
        use_structure=use_memory,
        use_pruner=False
    )

    result = search.search(
        f"problem_{index}"
    )

    return {
        "success": result["success"],
        "explored": result["explored"],
        "evaluated": result.get(
            "evaluated_candidates",
            0
        ),
        "generated": result.get(
            "generated_candidates",
            0
        ),
        "discarded": result.get(
            "discarded_candidates",
            0
        ),
        "depth": result.get(
            "depth",
            0
        ),
        "path": result.get(
            "path",
            []
        ),
        "graph": graph
    }


def main():

    repetitions = 10

    blind = []
    learned = []

    for i in range(repetitions):

        blind.append(
            run_problem(
                False,
                i
            )
        )

        learned.append(
            run_problem(
                True,
                i
            )
        )

    print()
    print("=" * 80)
    print(" BENCHMARK: TRANSITION MEMORY")
    print("=" * 80)
    print()
    print(f"{repetitions} problemas novos")
    print()

    print(
        f"{'ESTRATÉGIA':<25}"
        f"{'SOLUÇÕES':>10}"
        f"{'NÓS':>10}"
        f"{'AVALIADOS':>12}"
    )

    print("-" * 60)

    for name, results in [
        ("BUSCA CEGA", blind),
        ("TRANSITION MEMORY", learned)
    ]:

        solved = sum(
            item["success"]
            for item in results
        )

        nodes = sum(
            item["explored"]
            for item in results
        )

        evaluated = sum(
            item["evaluated"]
            for item in results
        )

        print(
            f"{name:<25}"
            f"{solved}/{repetitions:>7}"
            f"{nodes:>10}"
            f"{evaluated:>12}"
        )

    blind_eval = sum(
        item["evaluated"]
        for item in blind
    )

    learned_eval = sum(
        item["evaluated"]
        for item in learned
    )

    if blind_eval:
        reduction = (
            1 -
            learned_eval / blind_eval
        ) * 100
    else:
        reduction = 0

    print()
    print(
        f"Redução de avaliações: "
        f"{reduction:.2f}%"
    )

    print()
    print("PRIMEIRO CAMINHO APRENDIDO:")

    memory = learned[0]["graph"]
    transition_memory = TransitionMemory(
        memory
    )

    training_code = """def resolver(a, b):
    return (a - b, a + b)
"""

    priorities = transition_memory.mutation_priority(
        training_code
    )

    print(priorities)

    print()
    print("CAMINHO DO ÚLTIMO PROBLEMA:")

    for step in learned[-1]["path"]:
        print(
            f" -> {step}"
        )

    if not all(
        item["success"]
        for item in blind + learned
    ):
        raise SystemExit(
            "ERRO: alguma solução falhou."
        )

    print()
    print(
        "TRANSITION MEMORY: BENCHMARK CONCLUÍDO"
    )


if __name__ == "__main__":
    main()
