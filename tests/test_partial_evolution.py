from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine


graph = Graph()


source = """
def calcular(a, b):
    return a - b
"""


tests = """
TEST: assert candidate.calcular(10, 3) == 13
TEST: assert candidate.calcular(20, 5) == 25
TEST: assert candidate.calcular(7, 2) == 9
"""


add_code_node(
    graph,
    "problem_001",
    source,
    {
        "description": "problema evolutivo",
        "problem_type": "programming_problem"
    }
)


print("================================")
print(" MORPH-GRAPH PARTIAL FITNESS")
print("================================")


engine = EvolutionEngine(
    graph,
    tests=tests
)


result = engine.evolve(
    "problem_001",
    generations=5
)


print("\n=== RESULTADO ===")

final_id = result["final_node"]

print("Nó final:", final_id)

print(
    graph.nodes[
        final_id
    ]["data"]["code"]
)


print("\n=== EVOLUÇÃO ===")

for item in result["generations"]:

    selected = item["selected"]

    print(
        "Geração",
        item["generation"],
        "|",
        selected["rule"],
        "|",
        "score=",
        selected["score"]
    )
