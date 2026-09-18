from graph.core import Graph

from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.transition_memory import TransitionMemory
from engine.context_memory import ContextMemory


SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""


# ============================================================
# CONTEXTO A
# ============================================================

TRAIN_A = """
TEST: resolver(10, 3) == (7, 13)
TEST: resolver(20, 5) == (15, 25)
"""

NEW_A = """
TEST: resolver(8, 2) == (6, 10)
TEST: resolver(30, 4) == (26, 34)
"""


# ============================================================
# CONTEXTO B
# ============================================================

TRAIN_B = """
TEST: resolver(10, 3) == (13, 30)
TEST: resolver(4, 5) == (9, 20)
"""

NEW_B = """
TEST: resolver(7, 2) == (9, 14)
TEST: resolver(6, 4) == (10, 24)
"""


# ============================================================
# DESCOBRIR UMA TRAJETÓRIA
# ============================================================

def descobrir(graph, tests):

    mutator = AutomaticASTMutator()

    def evaluator(code):

        return evaluate_problem(
            code,
            tests
        ).as_dict()

    transition_memory = (
        TransitionMemory(graph)
    )

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        transition_memory=transition_memory
    )

    return search.search(
        "source"
    )


# ============================================================
# EXECUTAR NOVO PROBLEMA
# ============================================================

def executar(
    tests,
    context_memory=None
):

    graph = Graph()

    add_code_node(
        graph,
        "source",
        SOURCE,
        {
            "role": "source"
        }
    )

    mutator = AutomaticASTMutator()

    def evaluator(code):

        return evaluate_problem(
            code,
            tests
        ).as_dict()

    transition_memory = (
        TransitionMemory(graph)
    )

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        transition_memory=transition_memory,
        context_memory=context_memory,
        context_tests=tests
    )

    return search.search(
        "source"
    )


# ============================================================
# TREINAR MEMÓRIA CONTEXTUAL
# ============================================================

def treinar_contexto():

    graph = Graph()

    add_code_node(
        graph,
        "source",
        SOURCE,
        {
            "role": "source"
        }
    )

    # --------------------------------------------------------
    # A
    # --------------------------------------------------------

    result_a = descobrir(
        graph,
        TRAIN_A
    )

    if not result_a["success"]:
        raise RuntimeError(
            "Falha ao aprender A."
        )

    # --------------------------------------------------------
    # B
    # --------------------------------------------------------

    result_b = descobrir(
        graph,
        TRAIN_B
    )

    if not result_b["success"]:
        raise RuntimeError(
            "Falha ao aprender B."
        )

    # --------------------------------------------------------
    # MEMÓRIA
    # --------------------------------------------------------

    memory = ContextMemory(
        graph
    )

    memory.remember(
        TRAIN_A,
        result_a["path"],
        score=1.0
    )

    memory.remember(
        TRAIN_B,
        result_b["path"],
        score=1.0
    )

    return (
        graph,
        memory,
        result_a,
        result_b
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("MORPH-GRAPH")
    print("CONTEXTMEMORY + PATHSEARCH")
    print("=" * 70)

    # ========================================================
    # TREINAMENTO
    # ========================================================

    (
        memory_graph,
        context_memory,
        train_a,
        train_b
    ) = treinar_contexto()

    print()
    print("=" * 70)
    print("TRAJETÓRIAS APRENDIDAS")
    print("=" * 70)

    print(
        "A:",
        train_a["path"]
    )

    print(
        "B:",
        train_b["path"]
    )

    # ========================================================
    # SEM MEMÓRIA CONTEXTUAL
    # ========================================================

    print()
    print("=" * 70)
    print("SEM MEMÓRIA CONTEXTUAL")
    print("=" * 70)

    no_memory_a = executar(
        NEW_A
    )

    no_memory_b = executar(
        NEW_B
    )

    print()
    print("A")
    print(
        "Sucesso:",
        no_memory_a["success"]
    )
    print(
        "Caminho:",
        no_memory_a["path"]
    )
    print(
        "Avaliações:",
        no_memory_a[
            "evaluated_candidates"
        ]
    )
    print(
        "Descartados:",
        no_memory_a[
            "discarded_candidates"
        ]
    )

    print()
    print("B")
    print(
        "Sucesso:",
        no_memory_b["success"]
    )
    print(
        "Caminho:",
        no_memory_b["path"]
    )
    print(
        "Avaliações:",
        no_memory_b[
            "evaluated_candidates"
        ]
    )
    print(
        "Descartados:",
        no_memory_b[
            "discarded_candidates"
        ]
    )

    # ========================================================
    # COM MEMÓRIA CONTEXTUAL
    # ========================================================

    print()
    print("=" * 70)
    print("COM MEMÓRIA CONTEXTUAL")
    print("=" * 70)

    # --------------------------------------------------------
    # Importante:
    #
    # O ContextMemory foi aprendido no grafo de treinamento.
    # Para a busca nova, usamos um grafo novo, mas a memória
    # continua apontando para suas experiências aprendidas.
    # --------------------------------------------------------

    contextual_a = executar(
        NEW_A,
        context_memory
    )

    contextual_b = executar(
        NEW_B,
        context_memory
    )

    print()
    print("A")
    print(
        "Sucesso:",
        contextual_a["success"]
    )
    print(
        "Caminho:",
        contextual_a["path"]
    )
    print(
        "Avaliações:",
        contextual_a[
            "evaluated_candidates"
        ]
    )
    print(
        "Descartados:",
        contextual_a[
            "discarded_candidates"
        ]
    )

    print()
    print("B")
    print(
        "Sucesso:",
        contextual_b["success"]
    )
    print(
        "Caminho:",
        contextual_b["path"]
    )
    print(
        "Avaliações:",
        contextual_b[
            "evaluated_candidates"
        ]
    )
    print(
        "Descartados:",
        contextual_b[
            "discarded_candidates"
        ]
    )

    # ========================================================
    # MÉTRICAS
    # ========================================================

    no_memory_evaluations = (
        no_memory_a[
            "evaluated_candidates"
        ]
        +
        no_memory_b[
            "evaluated_candidates"
        ]
    )

    contextual_evaluations = (
        contextual_a[
            "evaluated_candidates"
        ]
        +
        contextual_b[
            "evaluated_candidates"
        ]
    )

    if no_memory_evaluations:

        reduction = (
            (
                len(no_memory_evaluations)
                    - len(contextual_evaluations)
            )
            /
            len(no_memory_evaluations)
        ) * 100

    else:

        reduction = 0.0

    success_no_memory = (
        int(no_memory_a["success"])
        +
        int(no_memory_b["success"])
    )

    success_contextual = (
        int(contextual_a["success"])
        +
        int(contextual_b["success"])
    )

    # ========================================================
    # RESULTADO
    # ========================================================

    print()
    print("=" * 70)
    print("RESULTADO")
    print("=" * 70)

    print(
        "Avaliações sem memória:",
        no_memory_evaluations
    )

    print(
        "Avaliações com contexto:",
        contextual_evaluations
    )

    print(
        "Redução da busca:",
        f"{reduction:.2f}%"
    )

    print(
        "Sucessos sem memória:",
        f"{success_no_memory}/2"
    )

    print(
        "Sucessos com contexto:",
        f"{success_contextual}/2"
    )

    print()
    print(
        "CAMINHO A SEM:",
        no_memory_a["path"]
    )

    print(
        "CAMINHO A COM:",
        contextual_a["path"]
    )

    print(
        "CAMINHO B SEM:",
        no_memory_b["path"]
    )

    print(
        "CAMINHO B COM:",
        contextual_b["path"]
    )

    # ========================================================
    # VALIDAÇÕES
    # ========================================================

    correct_a = (
        contextual_a["success"]
        and contextual_a["path"]
        == train_a["path"]
    )

    correct_b = (
        contextual_b["success"]
        and contextual_b["path"]
        == train_b["path"]
    )

    contextual_advantage = (
        len(contextual_evaluations)
            < len(no_memory_evaluations)
    )

    print()

    print(
        "SELEÇÃO CONTEXTUAL A:",
        "OK" if correct_a else "FALHOU"
    )

    print(
        "SELEÇÃO CONTEXTUAL B:",
        "OK" if correct_b else "FALHOU"
    )

    print(
        "SUCESSO COM CONTEXTO:",
        "OK"
        if success_contextual == 2
        else "FALHOU"
    )

    print(
        "VANTAGEM COMPUTACIONAL:",
        "OK"
        if contextual_advantage
        else "FALHOU"
    )

    if (
        correct_a
        and correct_b
        and success_contextual == 2
        and contextual_advantage
    ):

        print()
        print(
            "INTEGRAÇÃO CONTEXTMEMORY → PATHSEARCH: OK"
        )

    else:

        print()
        print(
            "INTEGRAÇÃO CONTEXTMEMORY → PATHSEARCH: "
            "AINDA INCOMPLETA"
        )


if __name__ == "__main__":
    main()
