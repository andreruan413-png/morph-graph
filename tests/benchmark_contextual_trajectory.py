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


def descobrir_trajetoria(
    tests
):

    graph = criar_grafo()

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
        transition_memory=TransitionMemory(
            graph
        )
    )

    return graph, search.search(
        "source"
    )


def construir_memoria():

    # -----------------------------------------------------
    # Descobre A
    # -----------------------------------------------------

    graph_a, result_a = descobrir_trajetoria(
        TESTS_A
    )

    if not result_a["success"]:
        raise RuntimeError(
            "Não foi possível aprender A."
        )

    # -----------------------------------------------------
    # Descobre B
    # -----------------------------------------------------

    graph_b, result_b = descobrir_trajetoria(
        TESTS_B
    )

    if not result_b["success"]:
        raise RuntimeError(
            "Não foi possível aprender B."
        )

    # -----------------------------------------------------
    # Memória compartilhada
    # -----------------------------------------------------

    memory = TransitionMemory(
        graph_a
    )

    memory.record_trajectory(
        SOURCE,
        result_a["path"],
        score=1.0
    )

    memory.record_search_result(
        "source",
        result_a["path"]
    )

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

    return memory, result_a, result_b


def testar_escolha(
    memory,
    tests,
    nome
):

    print("=" * 60)
    print(
        f"TESTANDO NOVO PROBLEMA: {nome}"
    )
    print("=" * 60)

    graph = criar_grafo()

    # -----------------------------------------------------
    # IMPORTANTE:
    #
    # A memória já contém duas trajetórias.
    #
    # Mas o problema atual ainda precisa ser resolvido.
    # -----------------------------------------------------

    memory.graph = graph

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
        "Caminho escolhido:",
        result["path"]
    )

    print(
        "Avaliações:",
        result["evaluated_candidates"]
    )

    return result


def main():

    print("=" * 60)
    print("MORPH-GRAPH")
    print("SELEÇÃO CONTEXTUAL DE TRAJETÓRIAS")
    print("=" * 60)

    # =====================================================
    # APRENDIZADO
    # =====================================================

    print("=" * 60)
    print("CONSTRUINDO MEMÓRIA")
    print("=" * 60)

    memory, result_a, result_b = construir_memoria()

    print(
        "Trajetória A:",
        result_a["path"]
    )

    print(
        "Trajetória B:",
        result_b["path"]
    )

    # =====================================================
    # MEMÓRIA
    # =====================================================

    print("=" * 60)
    print("TRAJETÓRIAS ARMAZENADAS")
    print("=" * 60)

    for index, trajectory in enumerate(
        memory.known_trajectories(SOURCE),
        start=1
    ):

        print(
            f"{index}.",
            trajectory["path"]
        )

    # =====================================================
    # NOVO PROBLEMA A
    # =====================================================

    result_test_a = testar_escolha(
        memory,
        TESTS_A,
        "OBJETIVO A"
    )

    # =====================================================
    # NOVO PROBLEMA B
    # =====================================================

    result_test_b = testar_escolha(
        memory,
        TESTS_B,
        "OBJETIVO B"
    )

    # =====================================================
    # ANÁLISE
    # =====================================================

    path_a = result_a["path"]
    path_b = result_b["path"]

    selected_a = result_test_a["path"]
    selected_b = result_test_b["path"]

    print("=" * 60)
    print("ANÁLISE DA SELEÇÃO")
    print("=" * 60)

    print(
        "Caminho correto para A:",
        path_a
    )

    print(
        "Caminho escolhido para A:",
        selected_a
    )

    print(
        "Caminho correto para B:",
        path_b
    )

    print(
        "Caminho escolhido para B:",
        selected_b
    )

    print("=" * 60)
    print("RESULTADO")
    print("=" * 60)

    if result_test_a["success"]:
        print(
            "OBJETIVO A RESOLVIDO: OK"
        )
    else:
        print(
            "OBJETIVO A RESOLVIDO: FALHOU"
        )

    if result_test_b["success"]:
        print(
            "OBJETIVO B RESOLVIDO: OK"
        )
    else:
        print(
            "OBJETIVO B RESOLVIDO: FALHOU"
        )

    if selected_a == path_a:
        print(
            "SELEÇÃO A CORRETA: OK"
        )
    else:
        print(
            "SELEÇÃO A CORRETA: FALHOU"
        )

    if selected_b == path_b:
        print(
            "SELEÇÃO B CORRETA: OK"
        )
    else:
        print(
            "SELEÇÃO B CORRETA: FALHOU"
        )

    print()
    print(
        "OBSERVAÇÃO:"
    )
    print(
        "Este teste mede a capacidade atual de "
        "reutilizar múltiplas trajetórias."
    )
    print(
        "Ele também revela se a memória atual "
        "já consegue distinguir contextos."
    )


if __name__ == "__main__":
    main()
