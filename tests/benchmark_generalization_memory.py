import os
import sys
import json

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.path_search import PathSearch
from engine.problem_evaluator import evaluate_problem
from engine.transition_memory import TransitionMemory


MEMORY_FILE = os.path.join(
    PROJECT_ROOT,
    "generalization_memory.json"
)


class CountingEvaluator:

    def __init__(self, tests):
        self.tests = tests
        self.count = 0

    def __call__(self, code):

        self.count += 1

        result = evaluate_problem(
            code,
            self.tests
        )

        return {
            "success": bool(result.success),
            "score": float(result.score),
            "reason": result.reason,
            "passed": result.passed,
            "total": result.total
        }


def criar_grafo(source_code, tests):

    graph = Graph()

    graph.add_node(
        "problem",
        "problem",
        {
            "description":
                "Resolver transformação algorítmica."
        }
    )

    graph.add_node(
        "specification",
        "specification",
        {
            "language": "python"
        }
    )

    graph.add_node(
        "tests",
        "tests",
        {
            "tests": tests
        }
    )

    graph.connect(
        "problem",
        "specification",
        "has_specification"
    )

    graph.connect(
        "problem",
        "tests",
        "has_tests"
    )

    graph.add_node(
        "source",
        "code",
        {
            "code": source_code,
            "language": "python"
        }
    )

    graph.connect(
        "problem",
        "source",
        "has_source"
    )

    return graph


def executar(
    source_code,
    tests,
    transition_memory=None
):

    graph = criar_grafo(
        source_code,
        tests
    )

    mutator = AutomaticASTMutator()

    evaluator = CountingEvaluator(
        tests
    )

    use_memory = (
        transition_memory is not None
    )

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=use_memory,
        use_structure=True,
        use_pruner=False,
        transition_memory=transition_memory
    )

    result = search.search(
        "source"
    )

    return {
        "success": result.get(
            "success",
            False
        ),
        "path": result.get(
            "path",
            []
        ),
        "evaluations": evaluator.count,
        "generated": result.get(
            "generated_candidates",
            0
        ),
        "discarded": result.get(
            "discarded_candidates",
            0
        )
    }


TRAINING_SOURCE = """def resolver(a, b):
    return (a - b, a + b)
"""


TRAINING_TESTS = """TEST: resolver(3, 2) == (5, 1)
TEST: resolver(10, 4) == (14, 6)
"""


PROBLEMS = [

    {
        "name": "PROBLEMA 1",
        "source": """def resolver(a, b):
    return (a - b, a + b)
""",
        "tests": """TEST: resolver(3, 2) == (5, 1)
TEST: resolver(10, 4) == (14, 6)
"""
    },

    {
        "name": "PROBLEMA 2",
        "source": """def calcular(x, y):
    return (x - y, x + y)
""",
        "tests": """TEST: calcular(3, 2) == (5, 1)
TEST: calcular(10, 4) == (14, 6)
"""
    },

    {
        "name": "PROBLEMA 3",
        "source": """def operar(p, q):
    return (p - q, p + q)
""",
        "tests": """TEST: operar(3, 2) == (5, 1)
TEST: operar(10, 4) == (14, 6)
"""
    },

    {
        "name": "PROBLEMA 4",
        "source": """def processar(n, m):
    return (n - m, n + m)
""",
        "tests": """TEST: processar(3, 2) == (5, 1)
TEST: processar(10, 4) == (14, 6)
"""
    }
]


def treinar_memoria():

    print()
    print("=" * 60)
    print("TREINAMENTO DA MEMÓRIA")
    print("=" * 60)

    graph = criar_grafo(
        TRAINING_SOURCE,
        TRAINING_TESTS
    )

    memory = TransitionMemory(
        graph
    )

    evaluator = CountingEvaluator(
        TRAINING_TESTS
    )

    search = PathSearch(
        graph=graph,
        mutator=AutomaticASTMutator(),
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=True,
        use_structure=True,
        use_pruner=False,
        transition_memory=memory
    )

    result = search.search(
        "source"
    )

    print(
        "Sucesso:",
        result["success"]
    )

    print(
        "Caminho:",
        result["path"]
    )

    print(
        "Avaliações:",
        evaluator.count
    )

    memory.export(
        MEMORY_FILE
    )

    print(
        "Memória exportada:",
        MEMORY_FILE
    )

    return memory


def main():

    print("=" * 60)
    print("MORPH-GRAPH")
    print("BENCHMARK DE GENERALIZAÇÃO DA MEMÓRIA")
    print("=" * 60)

    memory = treinar_memoria()

    print()
    print("=" * 60)
    print("CARREGANDO MEMÓRIA PERSISTENTE")
    print("=" * 60)

    new_graph = Graph()

    loaded_memory = TransitionMemory(
        new_graph
    )

    loaded_memory.load(
        MEMORY_FILE
    )

    print(
        "Memória carregada: OK"
    )

    print()

    resultados = []

    for problem in PROBLEMS:

        name = problem["name"]
        source = problem["source"]
        tests = problem["tests"]

        print("=" * 60)
        print(name)
        print("=" * 60)

        print()
        print("SEM MEMÓRIA...")

        baseline = executar(
            source,
            tests
        )

        print(
            "Sucesso:",
            baseline["success"]
        )

        print(
            "Caminho:",
            baseline["path"]
        )

        print(
            "Avaliações:",
            baseline["evaluations"]
        )

        print(
            "Gerados:",
            baseline["generated"]
        )

        print(
            "Descartados:",
            baseline["discarded"]
        )

        print()
        print("COM MEMÓRIA...")

        learned = executar(
            source,
            tests,
            transition_memory=loaded_memory
        )

        print(
            "Sucesso:",
            learned["success"]
        )

        print(
            "Caminho:",
            learned["path"]
        )

        print(
            "Avaliações:",
            learned["evaluations"]
        )

        print(
            "Gerados:",
            learned["generated"]
        )

        print(
            "Descartados:",
            learned["discarded"]
        )

        if baseline["evaluations"] > 0:

            reduction = (
                1
                - (
                    learned["evaluations"]
                    / baseline["evaluations"]
                )
            ) * 100

        else:

            reduction = 0.0

        print(
            "Redução:",
            f"{reduction:.2f}%"
        )

        resultados.append(
            {
                "name": name,
                "baseline": baseline,
                "memory": learned,
                "reduction": reduction
            }
        )

    print()
    print("=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)

    resolved = [
        item
        for item in resultados
        if (
            item["baseline"]["success"]
            and item["memory"]["success"]
        )
    ]

    if resolved:

        average_reduction = (
            sum(
                item["reduction"]
                for item in resolved
            )
            / len(resolved)
        )

    else:

        average_reduction = 0.0

    print(
        "Problemas resolvidos:",
        f"{len(resolved)}/{len(resultados)}"
    )

    print(
        "Redução média de avaliações:",
        f"{average_reduction:.2f}%"
    )

    if len(resolved) == len(resultados):

        print(
            "GENERALIZAÇÃO FUNCIONAL: OK"
        )

    else:

        print(
            "GENERALIZAÇÃO FUNCIONAL: "
            "NÃO COMPROVADA"
        )

    if (
        resolved
        and average_reduction > 0
    ):

        print(
            "VANTAGEM COMPUTACIONAL: OK"
        )

    else:

        print(
            "VANTAGEM COMPUTACIONAL: "
            "NÃO COMPROVADA"
        )

    with open(
        os.path.join(
            PROJECT_ROOT,
            "generalization_results.json"
        ),
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            resultados,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        "Resultados salvos em:",
        "generalization_results.json"
    )


if __name__ == "__main__":
    main()
