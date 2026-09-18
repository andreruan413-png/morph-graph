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
# DESCOBRIR TRAJETÓRIA
# ============================================================

def descobrir(graph, tests):

    mutator = AutomaticASTMutator()

    def evaluator(code):

        result = evaluate_problem(
            code,
            tests
        )

        return result.as_dict()

    memory = TransitionMemory(
        graph
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
        transition_memory=memory
    )

    return search.search(
        "source"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MORPH-GRAPH")
    print("MEMÓRIA CONTEXTUAL")
    print("=" * 60)

    # ========================================================
    # UM ÚNICO GRAFO
    # ========================================================

    graph = Graph()

    add_code_node(
        graph,
        "source",
        SOURCE,
        {
            "role": "source"
        }
    )

    # ========================================================
    # APRENDER A
    # ========================================================

    print()
    print("=" * 60)
    print("APRENDENDO CONTEXTO A")
    print("=" * 60)

    result_a = descobrir(
        graph,
        TRAIN_A
    )

    if not result_a["success"]:
        raise RuntimeError(
            "Não foi possível aprender A."
        )

    print(
        "Trajetória A:",
        result_a["path"]
    )

    # ========================================================
    # APRENDER B
    # ========================================================

    print()
    print("=" * 60)
    print("APRENDENDO CONTEXTO B")
    print("=" * 60)

    result_b = descobrir(
        graph,
        TRAIN_B
    )

    if not result_b["success"]:
        raise RuntimeError(
            "Não foi possível aprender B."
        )

    print(
        "Trajetória B:",
        result_b["path"]
    )

    # ========================================================
    # MEMÓRIA CONTEXTUAL
    # ========================================================

    context_memory = ContextMemory(
        graph
    )

    # ========================================================
    # REGISTRAR A
    # ========================================================

    context_memory.remember(
        TRAIN_A,
        result_a["path"],
        score=1.0
    )

    # ========================================================
    # REGISTRAR B
    # ========================================================

    context_memory.remember(
        TRAIN_B,
        result_b["path"],
        score=1.0
    )

    # ========================================================
    # ASSINATURAS
    # ========================================================

    signature_train_a = (
        context_memory.context_signature(
            TRAIN_A
        )
    )

    signature_new_a = (
        context_memory.context_signature(
            NEW_A
        )
    )

    signature_train_b = (
        context_memory.context_signature(
            TRAIN_B
        )
    )

    signature_new_b = (
        context_memory.context_signature(
            NEW_B
        )
    )

    print()
    print("=" * 60)
    print("ASSINATURAS CONTEXTUAIS")
    print("=" * 60)

    print(
        "A treinamento:",
        signature_train_a
    )

    print(
        "A novo:",
        signature_new_a
    )

    print(
        "B treinamento:",
        signature_train_b
    )

    print(
        "B novo:",
        signature_new_b
    )

    # ========================================================
    # GENERALIZAÇÃO
    # ========================================================

    same_a = (
        signature_train_a
        == signature_new_a
    )

    same_b = (
        signature_train_b
        == signature_new_b
    )

    different = (
        signature_train_a
        != signature_train_b
    )

    print()
    print("=" * 60)
    print("GENERALIZAÇÃO CONTEXTUAL")
    print("=" * 60)

    print(
        "A treinamento == A novo:",
        same_a
    )

    print(
        "B treinamento == B novo:",
        same_b
    )

    print(
        "A != B:",
        different
    )

    # ========================================================
    # RECUPERAÇÃO
    # ========================================================

    print()
    print("=" * 60)
    print("RECUPERAÇÃO DE TRAJETÓRIA")
    print("=" * 60)

    found_a = context_memory.trajectories_for(
        NEW_A
    )

    found_b = context_memory.trajectories_for(
        NEW_B
    )

    print(
        "Trajetórias recuperadas para A:"
    )

    for item in found_a:

        print(
            item["path"],
            "score=",
            item["score"]
        )

    print(
        "Trajetórias recuperadas para B:"
    )

    for item in found_b:

        print(
            item["path"],
            "score=",
            item["score"]
        )

    # ========================================================
    # SELEÇÃO
    # ========================================================

    best_a = context_memory.best_trajectory(
        NEW_A
    )

    best_b = context_memory.best_trajectory(
        NEW_B
    )

    print()
    print("=" * 60)
    print("SELEÇÃO CONTEXTUAL")
    print("=" * 60)

    print(
        "Melhor trajetória para A:",
        best_a["path"]
        if best_a
        else None
    )

    print(
        "Melhor trajetória para B:",
        best_b["path"]
        if best_b
        else None
    )

    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    correct_a = (
        best_a is not None
        and best_a["path"]
        == result_a["path"]
    )

    correct_b = (
        best_b is not None
        and best_b["path"]
        == result_b["path"]
    )

    # ========================================================
    # RESULTADO
    # ========================================================

    print()
    print("=" * 60)
    print("RESULTADO")
    print("=" * 60)

    print(
        "GENERALIZAÇÃO A:",
        "OK" if same_a else "FALHOU"
    )

    print(
        "GENERALIZAÇÃO B:",
        "OK" if same_b else "FALHOU"
    )

    print(
        "SEPARAÇÃO A/B:",
        "OK" if different else "FALHOU"
    )

    print(
        "SELEÇÃO A:",
        "OK" if correct_a else "FALHOU"
    )

    print(
        "SELEÇÃO B:",
        "OK" if correct_b else "FALHOU"
    )

    print()

    if (
        same_a
        and same_b
        and different
        and correct_a
        and correct_b
    ):

        print(
            "MEMÓRIA CONTEXTUAL: OK"
        )

    else:

        print(
            "MEMÓRIA CONTEXTUAL: "
            "AINDA INCOMPLETA"
        )


if __name__ == "__main__":
    main()
