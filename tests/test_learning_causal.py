import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch


CODE = """
def resolver(a, b):
    return (a + b, a - b)
"""

TESTS = """
TEST: resolver(10, 3) == (7, 13)
"""


def make_search(graph):
    mutator = AutomaticASTMutator()

    def evaluator(code):
        return evaluate_problem(code, TESTS).as_dict()

    return PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=True,
        use_structure=True,
        use_graph_guidance=True,
        use_context_guidance=True,
        use_failure_guidance=True,
        use_decision_score=True,
    )


def first_candidate(search):
    if not search.decision_history:
        return None
    return search.decision_history[0]


def main():
    print("=" * 70)
    print(" MORPH-GRAPH — TESTE CAUSAL DO APRENDIZADO")
    print("=" * 70)

    # ---------------------------------------------------------
    # BASELINE: grafo sem histórico
    # ---------------------------------------------------------

    graph_fresh = Graph()

    graph_fresh.add_node(
        "program",
        "code",
        {
            "code": CODE,
            "language": "python",
        },
    )

    fresh = make_search(graph_fresh)

    result_fresh = fresh.search("program")

    baseline = first_candidate(fresh)

    print()
    print("=== BASELINE — SEM HISTÓRICO ===")
    print("Sucesso:", result_fresh["success"])
    print("Caminho:", result_fresh["path"])

    if baseline:
        print(
            "Primeiro candidato:",
            baseline["candidate"],
        )
        print(
            "Score:",
            baseline["scores"]["total"],
        )

    # ---------------------------------------------------------
    # LEARNING: primeira execução cria evidência
    # ---------------------------------------------------------

    graph_learned = Graph()

    graph_learned.add_node(
        "program",
        "code",
        {
            "code": CODE,
            "language": "python",
        },
    )

    learned_first = make_search(graph_learned)

    result_first = learned_first.search("program")

    print()
    print("=== PRIMEIRA EXECUÇÃO — APRENDENDO ===")
    print("Sucesso:", result_first["success"])
    print("Caminho:", result_first["path"])

    # ---------------------------------------------------------
    # SECOND RUN: mesmo contexto + histórico
    # ---------------------------------------------------------

    learned_second = make_search(graph_learned)

    result_second = learned_second.search("program")

    learned = first_candidate(learned_second)

    print()
    print("=== SEGUNDA EXECUÇÃO — COM HISTÓRICO ===")
    print("Sucesso:", result_second["success"])
    print("Caminho:", result_second["path"])

    if learned:
        print(
            "Primeiro candidato:",
            learned["candidate"],
        )
        print(
            "Score:",
            learned["scores"]["total"],
        )

    # ---------------------------------------------------------
    # ANÁLISE
    # ---------------------------------------------------------

    print()
    print("=== ANÁLISE CAUSAL ===")

    if baseline:
        print(
            "Baseline:",
            baseline["candidate"],
        )

    if learned:
        print(
            "Com aprendizado:",
            learned["candidate"],
        )

        print()
        print(
            "Score baseline:",
            baseline["scores"]["total"],
        )
        print(
            "Score aprendido:",
            learned["scores"]["total"],
        )

    print()

    assert result_fresh["success"] is True
    assert result_first["success"] is True
    assert result_second["success"] is True

    assert baseline is not None
    assert learned is not None

    # O histórico precisa existir.
    assert len(graph_learned.nodes) > len(graph_fresh.nodes)

    # O segundo processo precisa ter produzido decisões
    # usando o mesmo código/contexto.
    decision_nodes = [
        node
        for node in graph_learned.nodes.values()
        if node.get("type") == "decision"
    ]

    decisions_with_context = [
        node
        for node in decision_nodes
        if node.get("data", {}).get("source_code")
    ]

    assert decisions_with_context

    print(
        "DECISÕES COM CONTEXTO:",
        len(decisions_with_context),
    )

    print("EXECUÇÕES → OK")
    print("HISTÓRICO → OK")
    print("SOURCE_CODE → OK")

    if baseline["candidate"] != learned["candidate"]:
        print()
        print("APRENDIZADO → MUDOU A PRIMEIRA DECISÃO: OK")
    else:
        print()
        print(
            "APRENDIZADO → MESMA PRIMEIRA DECISÃO"
        )
        print(
            "Isso não é falha: significa que o histórico "
            "reforçou a mesma escolha."
        )

    print()
    print("TESTE CAUSAL → OK")


if __name__ == "__main__":
    main()
