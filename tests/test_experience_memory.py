from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine
from engine.experience_memory import ExperienceMemory


graph = Graph()


# ============================================================
# PRIMEIRO PROBLEMA
# ============================================================

problem_a = Problem(
    "problem_memory_a",
    "Criar uma função que some dois números.",
    """
TEST: assert candidate.calcular(2, 3) == 5
TEST: assert candidate.calcular(10, 7) == 17
TEST: assert candidate.calcular(20, 5) == 25
"""
)

problem_a.add_to_graph(graph)


add_code_node(
    graph,
    "candidate_memory_a",
    """
def calcular(a, b):
    return a - b
"""
)


graph.connect(
    "problem_memory_a",
    "candidate_memory_a",
    "has_candidate"
)


engine_a = ProblemEngine(
    graph,
    "problem_memory_a"
)


result_a = engine_a.solve(
    generations=5
)


print()
print("=== PRIMEIRA EXPERIÊNCIA ===")
print(
    "Solução:",
    result_a["final_node"]
)

print(
    "Score:",
    result_a["final_score"]
)

print(
    "Experiência:",
    result_a["experience_node"]
)


# ============================================================
# NOVO PROGRAMA
# ============================================================

new_code = """
def resolver(x, y):
    return x - y
"""


memory = ExperienceMemory(
    graph
)


matches = memory.find_similar_experiences(
    new_code
)


print()
print("=== EXPERIÊNCIAS SEMELHANTES ===")

for match in matches:

    print(
        f"{match['experience_id']} | "
        f"similaridade="
        f"{match['similarity']:.2f} | "
        f"score="
        f"{match['score']:.2f}"
    )


mutations = memory.mutation_history(
    new_code
)


print()
print("=== MUTAÇÕES RECUPERADAS ===")

for mutation in mutations:

    print(
        f"{mutation['rule']} | "
        f"similaridade="
        f"{mutation['similarity']:.2f} | "
        f"score="
        f"{mutation['score']:.2f}"
    )


assert result_a["final_score"] == 1.0

assert len(matches) >= 1

assert len(mutations) >= 1

assert mutations[0]["rule"] == (
    "binop_0_sub_to_add"
)


print()
print("MEMÓRIA CONSULTÁVEL: OK")
