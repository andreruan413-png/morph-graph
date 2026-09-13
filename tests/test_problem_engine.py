from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine


graph = Graph()


problem = Problem(
    "problem_002",
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
    "candidate_002",
    """
def calcular(a, b):
    return a - b
"""
)


graph.connect(
    "problem_002",
    "candidate_002",
    "has_candidate"
)


engine = ProblemEngine(
    graph,
    "problem_002"
)


result = engine.solve(
    generations=5
)


print()
print("=== RESULTADO FINAL ===")
print(
    f"Nó final: {result['final_node']}"
)
print(
    f"Score final: {result['final_score']}"
)

print()
print("=== EVOLUÇÕES ===")

for generation in result["generations"]:

    selected = generation[
        "selected"
    ]

    print(
        f"Geração {generation['generation']}: "
        f"{selected['rule']} -> "
        f"score={selected['score']}"
    )

print()
print("=== RELAÇÕES DO PROBLEMA ===")

for edge in graph.edges:

    if edge["source"] == "problem_002":

        print(
            f"{edge['source']} "
            f"--[{edge['relation']}]--> "
            f"{edge['target']}"
        )
