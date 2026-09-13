from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine


graph = Graph()


problem = Problem(
    "problem_003",
    "Criar uma função calcular que some dois números.",
    """
TEST: assert candidate.calcular(2, 3) == 5
TEST: assert candidate.calcular(10, 7) == 17
TEST: assert candidate.calcular(20, 5) == 25
"""
)

problem.add_to_graph(graph)


add_code_node(
    graph,
    "candidate_003",
    """
def calcular(a, b):
    return a - b
"""
)


graph.connect(
    "problem_003",
    "candidate_003",
    "has_candidate"
)


engine = ProblemEngine(
    graph,
    "problem_003"
)


result = engine.solve(
    generations=5
)


print()
print("=== SOLUÇÃO ===")
print(
    "Nó final:",
    result["final_node"]
)

print(
    "Score:",
    result["final_score"]
)

print(
    "Experiência:",
    result["experience_node"]
)


print()
print("=== EXPERIÊNCIA REGISTRADA ===")

experience = graph.nodes[
    result["experience_node"]
]

print(
    "ID:",
    experience["id"]
)

print(
    "Tipo:",
    experience["type"]
)

print(
    "Problema:",
    experience["data"]["problem_id"]
)

print(
    "Solução:",
    experience["data"]["solution_node"]
)

print(
    "Score:",
    experience["data"]["score"]
)


print()
print("=== GRAFO DE EXPERIÊNCIA ===")

for edge in graph.edges:

    if (
        edge["source"]
        == result["experience_node"]
    ):

        print(
            f"{edge['source']} "
            f"--[{edge['relation']}]--> "
            f"{edge['target']}"
        )
