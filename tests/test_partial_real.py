from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine


graph = Graph()


source = """
def calcular(a, b):
    if a > 0:
        return a - b
    return a - b
"""


tests = """
TEST: assert candidate.calcular(10, 3) == 13
TEST: assert candidate.calcular(20, 5) == 25
TEST: assert candidate.calcular(-2, 5) == -7
"""


add_code_node(
    graph,
    "problem_001",
    source
)


engine = EvolutionEngine(
    graph,
    tests=tests
)


result = engine.evolve(
    "problem_001",
    generations=8
)


print("\n=== RESULTADO FINAL ===")

final_id = result["final_node"]

print("Nó:", final_id)

print(
    graph.nodes[final_id]["data"]["code"]
)


print("\n=== TRAJETÓRIA ===")

for item in result["generations"]:

    selected = item["selected"]

    print(
        f"Geração {item['generation']}: "
        f"{selected['rule']} "
        f"score={selected['score']}"
    )
