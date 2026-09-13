from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine


graph = Graph()

source = """
def calcular(a, b):
    return a - b

assert calcular(10, 3) == 13
"""

add_code_node(
    graph,
    "problem_001",
    source,
    {
        "description": "Encontrar uma implementação que satisfaça o teste",
        "problem_type": "programming_problem"
    }
)

print("================================")
print(" MORPH-GRAPH PROBLEM EVOLUTION")
print("================================")

print("\nPROBLEMA:")
print("calcular(10, 3) deve retornar 13")

engine = EvolutionEngine(graph)

result = engine.evolve(
    "problem_001",
    generations=3
)

print("\n=== RESULTADO ===")

final_id = result["final_node"]

print("Nó final:", final_id)

print(
    graph.nodes[
        final_id
    ]["data"]["code"]
)

print("\nNós:", len(graph.nodes))
print("Conexões:", len(graph.edges))
