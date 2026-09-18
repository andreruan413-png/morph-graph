from graph.core import Graph

from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.transition_memory import TransitionMemory


MEMORY_FILE = "trajectory_choices_memory.json"


SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""


# ---------------------------------------------------------
# PROBLEMA A
# ---------------------------------------------------------
#
# Caminho desejado:
#
# add -> sub
# sub -> add
#
# Resultado:
# (a - b, a + b)
#
# ---------------------------------------------------------

TESTS_A = """
TEST: resolver(10, 3) == (7, 13)
TEST: resolver(20, 5) == (15, 25)
"""


# ---------------------------------------------------------
# PROBLEMA B
# ---------------------------------------------------------
#
# Outro caminho válido a partir da mesma estrutura:
#
# sub -> mult
#
# Resultado:
# (a + b, a * b)
#
# ---------------------------------------------------------

TESTS_B = """
TEST: resolver(10, 3) == (13, 30)
TEST: resolver(4, 5) == (9, 20)
"""


def criar_grafo(source_code):
    graph = Graph()

    add_code_node(
        graph,
        "source",
        source_code,
        {
            "role": "source"
        }
    )

    return graph


def executar(source_code, tests, transition_memory=None):

    graph = criar_grafo(source_code)

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
        transition_memory=transition_memory
    )

    result = search.search(
        "source"
    )

    return graph, result


def treinar_problema(nome, tests):

    print("=" * 60)
    print(f"TREINAMENTO: {nome}")
    print("=" * 60)

    graph, result = executar(
        SOURCE,
        tests
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
        result["evaluated_candidates"]
    )

    return graph, result


def main():

    print("=" * 60)
    print("MORPH-GRAPH")
    print("BENCHMARK DE TRAJETÓRIAS ALTERNATIVAS")
    print("=" * 60)

    # -----------------------------------------------------
    # TREINAMENTO 1
    # -----------------------------------------------------

    graph_a, result_a = treinar_problema(
        "PROBLEMA A",
        TESTS_A
    )

    if not result_a["success"]:
        print(
            "\nERRO: problema A não foi resolvido."
        )
        return

    memory_a = TransitionMemory(
        graph_a
    )

    memory_a.record_trajectory(
        SOURCE,
        result_a["path"]
    )

    memory_a.record_search_result(
        "source",
        result_a["path"]
    )

    # -----------------------------------------------------
    # EXPORTA PRIMEIRA EXPERIÊNCIA
    # -----------------------------------------------------

    memory_a.export(
        MEMORY_FILE
    )

    print(
        "\nMemória após problema A:"
    )

    print(
        memory_a.trajectories
    )

    print(
        memory_a.trajectory_steps
    )

    # -----------------------------------------------------
    # TREINAMENTO 2
    # -----------------------------------------------------

    graph_b, result_b = treinar_problema(
        "PROBLEMA B",
        TESTS_B
    )

    if not result_b["success"]:
        print(
            "\nERRO: problema B não foi resolvido."
        )
        return

    memory_b = TransitionMemory(
        graph_b
    )

    memory_b.record_trajectory(
        SOURCE,
        result_b["path"]
    )

    memory_b.record_search_result(
        "source",
        result_b["path"]
    )

    # -----------------------------------------------------
    # MOSTRA A SEGUNDA TRAJETÓRIA
    # -----------------------------------------------------

    print(
        "\nMemória do problema B:"
    )

    print(
        memory_b.trajectories
    )

    # -----------------------------------------------------
    # COMPARAÇÃO
    # -----------------------------------------------------

    print("=" * 60)
    print("COMPARAÇÃO DAS TRAJETÓRIAS")
    print("=" * 60)

    print(
        "Trajetória A:",
        result_a["path"]
    )

    print(
        "Trajetória B:",
        result_b["path"]
    )

    if result_a["path"] != result_b["path"]:

        print(
            "\nTRAJETÓRIAS DIFERENTES: OK"
        )

    else:

        print(
            "\nTRAJETÓRIAS DIFERENTES: FALHOU"
        )

    # -----------------------------------------------------
    # TESTE DA LIMITAÇÃO ATUAL
    # -----------------------------------------------------

    print("=" * 60)
    print("TESTANDO MEMÓRIA ATUAL")
    print("=" * 60)

    learned = TransitionMemory(
        graph_a
    )

    learned.record_trajectory(
        SOURCE,
        result_a["path"]
    )

    learned.record_search_result(
        "source",
        result_a["path"]
    )

    print(
        "Trajetória armazenada:",
        learned.trajectories
    )

    priorities = learned.mutation_priority(
        SOURCE
    )

    print(
        "Prioridades:",
        priorities
    )

    print("=" * 60)
    print("RESULTADO")
    print("=" * 60)

    print(
        "O benchmark mostrou que duas soluções "
        "podem partir da mesma estrutura."
    )

    print(
        "O próximo passo será permitir que "
        "TransitionMemory armazene múltiplas "
        "trajetórias para a mesma assinatura."
    )

    print(
        "\nMemória atual ainda é limitada a "
        "uma trajetória principal por assinatura."
    )


if __name__ == "__main__":
    main()
