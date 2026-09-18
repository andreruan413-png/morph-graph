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
    "two_step_memory.json"
)


SOURCE_CODE = """def resolver(a, b):
    return (a - b, a + b)
"""

TEST_CODE = """TEST: resolver(3, 2) == (5, 1)
TEST: resolver(10, 4) == (14, 6)
"""


class CountingEvaluator:

    def __init__(self):
        self.count = 0

    def __call__(self, code):

        self.count += 1

        result = evaluate_problem(
            code,
            TEST_CODE
        )

        return {
            "success": bool(result.success),
            "score": float(result.score),
            "reason": result.reason
        }


def criar_grafo():

    graph = Graph()

    graph.add_node(
        "problem",
        "problem",
        {
            "description":
                "Problema que exige múltiplas "
                "transformações."
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
            "tests": TEST_CODE
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
            "code": SOURCE_CODE,
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
    use_memory=False,
    transition_memory=None
):

    graph = criar_grafo()

    mutator = AutomaticASTMutator()

    evaluator = CountingEvaluator()

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
        "success":
            result.get(
                "success",
                False
            ),
        "path":
            result.get(
                "path",
                []
            ),
        "evaluations":
            evaluator.count,
        "generated":
            result.get(
                "generated_candidates",
                0
            ),
        "discarded":
            result.get(
                "discarded_candidates",
                0
            ),
        "graph":
            graph
    }


def treinar():

    print()
    print("========================================")
    print(" TREINAMENTO DA TRAJETÓRIA")
    print("========================================")

    graph = criar_grafo()

    mutator = AutomaticASTMutator()

    evaluator = CountingEvaluator()

    memory = TransitionMemory(
        graph
    )

    search = PathSearch(
        graph=graph,
        mutator=mutator,
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

    path = result.get(
        "path",
        []
    )

    print(
        f"Sucesso: "
        f"{result.get('success', False)}"
    )

    print(
        f"Caminho aprendido: "
        f"{path}"
    )

    print(
        f"Avaliações no treinamento: "
        f"{evaluator.count}"
    )

    if not result.get("success", False):

        print()
        print(
            "ERRO: o problema de treinamento "
            "não foi resolvido."
        )

        return None

    memory.record_trajectory(
        SOURCE_CODE,
        path
    )

    memory.record_search_result(
        "source",
        path
    )

    exported = memory.export(
        MEMORY_FILE
    )

    print()
    print(
        f"Memória exportada: "
        f"{MEMORY_FILE}"
    )

    print()
    print("Memória aprendida:")

    print(
        json.dumps(
            exported,
            indent=2,
            ensure_ascii=False
        )
    )

    return memory


def imprimir_resultado(
    nome,
    resultado
):

    print()
    print("========================================")
    print(nome)
    print("========================================")

    print(
        f"Sucesso: "
        f"{resultado['success']}"
    )

    print(
        f"Caminho: "
        f"{resultado['path']}"
    )

    print(
        f"Avaliações: "
        f"{resultado['evaluations']}"
    )

    print(
        f"Candidatos gerados: "
        f"{resultado['generated']}"
    )

    print(
        f"Candidatos descartados: "
        f"{resultado['discarded']}"
    )


def main():

    print()
    print("========================================")
    print(" MORPH-GRAPH")
    print(" BENCHMARK DE TRAJETÓRIA")
    print("========================================")

    # ------------------------------------
    # TREINAMENTO
    # ------------------------------------

    memory = treinar()

    if memory is None:
        return

    # ------------------------------------
    # BASELINE
    # ------------------------------------

    print()
    print(
        "Executando busca SEM memória..."
    )

    baseline = executar(
        use_memory=False
    )

    imprimir_resultado(
        "SEM MEMÓRIA",
        baseline
    )

    # ------------------------------------
    # NOVO GRAFO + LOAD
    # ------------------------------------

    print()
    print(
        "Criando novo estado..."
    )

    novo_grafo = criar_grafo()

    loaded_memory = TransitionMemory(
        novo_grafo
    )

    loaded_memory.load(
        MEMORY_FILE
    )

    print(
        "Memória persistente carregada: OK"
    )

    print(
        f"Próximo passo aprendido: "
        f"{loaded_memory.learned_next_step(SOURCE_CODE)}"
    )

    # ------------------------------------
    # BUSCA COM MEMÓRIA
    # ------------------------------------

    print()
    print(
        "Executando busca COM memória..."
    )

    learned = executar(
        use_memory=True,
        transition_memory=loaded_memory
    )

    imprimir_resultado(
        "COM MEMÓRIA",
        learned
    )

    # ------------------------------------
    # COMPARAÇÃO
    # ------------------------------------

    print()
    print("========================================")
    print(" COMPARAÇÃO")
    print("========================================")

    base_eval = baseline[
        "evaluations"
    ]

    learned_eval = learned[
        "evaluations"
    ]

    print(
        f"Avaliações sem memória: "
        f"{base_eval}"
    )

    print(
        f"Avaliações com memória: "
        f"{learned_eval}"
    )

    if base_eval > 0:

        reduction = (
            1
            - (
                learned_eval
                / base_eval
            )
        ) * 100

        print(
            f"Redução de avaliações: "
            f"{reduction:.2f}%"
        )

    else:

        print(
            "Redução de avaliações: "
            "não calculável"
        )

    print()

    if (
        baseline["success"]
        and learned["success"]
    ):

        print(
            "AMBAS RESOLVERAM: OK"
        )

    else:

        print(
            "AMBAS RESOLVERAM: FALHOU"
        )

    print()

    if learned_eval < base_eval:

        print(
            "VANTAGEM DA MEMÓRIA: OK"
        )

    elif learned_eval == base_eval:

        print(
            "VANTAGEM DA MEMÓRIA: "
            "AINDA NÃO COMPROVADA"
        )

    else:

        print(
            "VANTAGEM DA MEMÓRIA: "
            "MEMÓRIA USOU MAIS AVALIAÇÕES"
        )

    print()
    print(
        "Benchmark finalizado."
    )


if __name__ == "__main__":
    main()
