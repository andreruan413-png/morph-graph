import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.problem import Problem
from engine.problem_engine import ProblemEngine
from engine.experience_memory import ExperienceMemory
from engine.trajectory_guidance import TrajectoryGuidance


def add_candidate(graph, problem_id, code):
    candidate_id = f"{problem_id}_candidate"

    graph.add_node(
        candidate_id,
        "code",
        {
            "code": code,
            "language": "python"
        }
    )

    graph.connect(
        problem_id,
        candidate_id,
        "has_candidate"
    )

    return candidate_id


def main():

    graph = Graph()

    # =========================================================
    # PROBLEMA A
    # =========================================================

    problem_a = Problem(
        "problem_a",
        "Retornar soma e multiplicação.",
        """
TEST: assert calcular(2, 3)[0] == 5
TEST: assert calcular(2, 3)[1] == 6
"""
    )

    problem_a.add_to_graph(graph)

    candidate_a = add_candidate(
        graph,
        "problem_a",
        """
def calcular(a, b):
    return (a - b, a + b)
"""
    )

    print()
    print("=== APRENDIZAGEM: PROBLEMA A ===")

    engine_a = ProblemEngine(
        graph,
        "problem_a"
    )

    result_a = engine_a.solve(
        generations=3
    )

    print("Sucesso:", result_a["final_score"] == 1.0)
    print("Score:", result_a["final_score"])
    print("Experiência:", result_a["experience_node"])

    assert result_a["final_score"] == 1.0
    assert result_a["experience_node"] is not None

    # =========================================================
    # MEMÓRIA APÓS A PRIMEIRA SOLUÇÃO
    # =========================================================

    memory = ExperienceMemory(graph)

    similar = memory.find_similar_experiences(
        """
def resolver(x, y):
    return (x - y, x + y)
"""
    )

    guidance = TrajectoryGuidance(graph)

    first_step = guidance.priorities([])

    print()
    print("=== MEMÓRIA APÓS PROBLEMA A ===")
    print("Experiências similares:", len(similar))
    print("Próximo passo aprendido:", first_step)

    assert len(similar) >= 1
    assert "binop_0_sub_to_add" in first_step

    # =========================================================
    # PROBLEMA B
    # =========================================================

    problem_b = Problem(
        "problem_b",
        "Retornar soma e multiplicação para outra função.",
        """
TEST: assert resolver(10, 5)[0] == 15
TEST: assert resolver(10, 5)[1] == 50
"""
    )

    problem_b.add_to_graph(graph)

    candidate_b = add_candidate(
        graph,
        "problem_b",
        """
def resolver(x, y):
    return (x - y, x + y)
"""
    )

    print()
    print("=== PROBLEMA B ===")

    # Consulta a trajetória ANTES de resolver.
    learned = guidance.priorities([])

    print(
        "Regra priorizada:",
        max(
            learned,
            key=learned.get
        )
    )

    assert (
        max(
            learned,
            key=learned.get
        )
        == "binop_0_sub_to_add"
    )

    # =========================================================
    # CONFIRMAÇÃO ESTRUTURAL
    # =========================================================

    mutator = AutomaticASTMutator()

    candidates = mutator.generate(
        graph.nodes[candidate_b]["data"]["code"]
    )

    names = [
        candidate.name
        for candidate in candidates
    ]

    print()
    print("=== CANDIDATOS DO PROBLEMA B ===")

    for name in names:
        print(" -", name)

    assert "binop_0_sub_to_add" in names

    print()
    print("================================")
    print("APRENDIZAGEM END-TO-END: OK")
    print("================================")


if __name__ == "__main__":
    main()
