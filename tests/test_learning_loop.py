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


def make_search(graph, tests):
    mutator = AutomaticASTMutator()

    def evaluator(code):
        result = evaluate_problem(code, tests)
        return result.as_dict()

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


def main():
    graph = Graph()

    code_a = """
def calcular(a, b):
    return (a + b, a - b)
"""

    tests_a = """
TEST: calcular(10, 3) == (7, 13)
"""

    graph.add_node(
        "program_a",
        "code",
        {
            "code": code_a,
            "language": "python",
        },
    )

    print("=" * 70)
    print(" MORPH-GRAPH — CICLO REAL DE APRENDIZADO")
    print("=" * 70)

    print()
    print("=== PRIMEIRA EXECUÇÃO ===")

    search_a = make_search(graph, tests_a)
    result_a = search_a.search("program_a")

    print("Sucesso:", result_a["success"])
    print("Caminho:", result_a["path"])
    print("Decisões:", len(
        [
            node
            for node in graph.nodes.values()
            if node.get("type") == "decision"
        ]
    ))
    print("Experiências:", len(
        [
            node
            for node in graph.nodes.values()
            if node.get("type") == "experience"
        ]
    ))

    assert result_a["success"] is True

    print()
    print("=== SEGUNDA EXECUÇÃO — CONTEXTO SEMELHANTE ===")

    code_b = """
def resolver(x, y):
    return (x + y, x - y)
"""

    tests_b = """
TEST: resolver(20, 5) == (15, 25)
"""

    graph.add_node(
        "program_b",
        "code",
        {
            "code": code_b,
            "language": "python",
        },
    )

    search_b = make_search(graph, tests_b)
    result_b = search_b.search("program_b")

    print("Sucesso:", result_b["success"])
    print("Caminho:", result_b["path"])

    decisions = [
        node
        for node in graph.nodes.values()
        if node.get("type") == "decision"
    ]

    print()
    print("=== DECISÕES REGISTRADAS ===")

    for decision in decisions:
        data = decision["data"]
        print(
            decision["id"],
            "|",
            data.get("candidate"),
            "|",
            data.get("outcome"),
            "| contexto:",
            bool(data.get("source_code")),
        )

    assert result_b["success"] is True

    decisions_with_context = [
        decision
        for decision in decisions
        if decision["data"].get("source_code")
    ]

    assert decisions_with_context

    print()
    print("DECISÕES COM SOURCE_CODE:", len(decisions_with_context))
    print("PRIMEIRA SOLUÇÃO:", result_a["path"])
    print("SEGUNDA SOLUÇÃO:", result_b["path"])

    print()
    print("LEARNING LOOP → OK")


if __name__ == "__main__":
    main()
