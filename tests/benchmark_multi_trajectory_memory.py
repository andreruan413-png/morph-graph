from graph.core import Graph

from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.transition_memory import TransitionMemory


SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""


TESTS_A = """
TEST: resolver(10, 3) == (7, 13)
TEST: resolver(20, 5) == (15, 25)
"""


TESTS_B = """
TEST: resolver(10, 3) == (13, 30)
TEST: resolver(4, 5) == (9, 20)
"""


def criar_grafo():

    graph = Graph()

    add_code_node(
        graph,
        "source",
        SOURCE,
        {
            "role": "source"
        }
    )

    return graph


def executar(
    graph,
    tests,
    memory=None
):

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
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        transition_memory=(
            memory
            if memory is not None
            else TransitionMemory(graph)
        )
    )

    return search.search(
        "source"
    )


def main():

    print("=" * 60)
    print("MORPH-GRAPH")
    print("MEMÓRIA DE MÚLTIPLAS TRAJETÓRIAS")
    print("=" * 60)

    # =====================================================
    # UMA ÚNICA MEMÓRIA FINAL
    # =====================================================

    memory = TransitionMemory(
        criar_grafo()
    )

    # =====================================================
    # TREINAMENTO A
    # =====================================================

    print("=" * 60)
    print("APRENDENDO TRAJETÓRIA A")
    print("=" * 60)

    graph_a = criar_grafo()

    result_a = executar(
        graph_a,
        TESTS_A
    )

    print(
        "Sucesso:",
        result_a["success"]
    )

    print(
        "Caminho:",
        result_a["path"]
    )

    if not result_a["success"]:

        print(
            "ERRO: problema A não foi resolvido."
        )

        return

    # Adicionamos A à memória compartilhada.
    memory.graph = graph_a

    memory.record_trajectory(
        SOURCE,
        result_a["path"],
        score=1.0
    )

    memory.record_search_result(
        "source",
        result_a["path"]
    )

    # =====================================================
    # TREINAMENTO B
    # =====================================================

    print("=" * 60)
    print("APRENDENDO TRAJETÓRIA B")
    print("=" * 60)

    graph_b = criar_grafo()

    # IMPORTANTE:
    #
    # B precisa poder descobrir uma trajetória diferente.
    #
    # Portanto, durante esta etapa de descoberta,
    # não usamos a memória A como filtro.
    #
    result_b = executar(
        graph_b,
        TESTS_B
    )

    print(
        "Sucesso:",
        result_b["success"]
    )

    print(
        "Caminho:",
        result_b["path"]
    )

    if not result_b["success"]:

        print(
            "ERRO: problema B não foi resolvido."
        )

        return

    # Agora adicionamos B à MESMA memória.
    memory.graph = graph_b

    memory.record_trajectory(
        SOURCE,
        result_b["path"],
        score=1.0
    )

    memory.record_search_result(
        "source",
        result_b["path"]
    )

    # =====================================================
    # MEMÓRIA FINAL
    # =====================================================

    print("=" * 60)
    print("MEMÓRIA FINAL")
    print("=" * 60)

    known = memory.known_trajectories(
        SOURCE
    )

    for index, trajectory in enumerate(
        known,
        start=1
    ):

        print(
            f"\nTRAJETÓRIA {index}"
        )

        print(
            "Path:",
            trajectory["path"]
        )

        print(
            "Count:",
            trajectory["count"]
        )

        print(
            "Score:",
            trajectory["score"]
        )

    # =====================================================
    # PRIMEIRO PASSO
    # =====================================================

    print("=" * 60)
    print("PRIMEIRO PASSO")
    print("=" * 60)

    first_steps = memory.next_steps(
        SOURCE
    )

    print(
        first_steps
    )

    # =====================================================
    # SEGUNDO PASSO
    # =====================================================

    prefix = [
        "binop_1_sub_to_add"
    ]

    print("=" * 60)
    print(
        "SEGUNDO PASSO APÓS:",
        prefix
    )
    print("=" * 60)

    second_steps = memory.next_steps(
        SOURCE,
        prefix
    )

    print(
        second_steps
    )

    # =====================================================
    # VALIDAÇÃO
    # =====================================================

    print("=" * 60)
    print("VALIDAÇÃO")
    print("=" * 60)

    paths = [
        trajectory["path"]
        for trajectory in known
    ]

    path_a = result_a["path"]
    path_b = result_b["path"]

    if path_a in paths:

        print(
            "TRAJETÓRIA A ARMAZENADA: OK"
        )

    else:

        print(
            "TRAJETÓRIA A ARMAZENADA: FALHOU"
        )

    if path_b in paths:

        print(
            "TRAJETÓRIA B ARMAZENADA: OK"
        )

    else:

        print(
            "TRAJETÓRIA B ARMAZENADA: FALHOU"
        )

    if len(known) >= 2:

        print(
            "MÚLTIPLAS TRAJETÓRIAS: OK"
        )

    else:

        print(
            "MÚLTIPLAS TRAJETÓRIAS: FALHOU"
        )

    if second_steps.get("binop_0_add_to_sub", 0.0) > 0.0:

        print(
            "PRÓXIMO PASSO CONDICIONAL: OK"
        )

    else:

        print(
            "PRÓXIMO PASSO CONDICIONAL: FALHOU"
        )

    if (
        result_a["success"]
        and result_b["success"]
    ):

        print(
            "AMBOS OS PROBLEMAS: OK"
        )

    else:

        print(
            "AMBOS OS PROBLEMAS: FALHOU"
        )


if __name__ == "__main__":
    main()
