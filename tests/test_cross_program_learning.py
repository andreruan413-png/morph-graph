from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine
from engine.strategy import mutation_statistics


graph = Graph()

program_a = """
def soma(a, b):
    return a + b

assert soma(2, 3) == 5
"""

add_code_node(
    graph,
    "program_a",
    program_a,
    {
        "description": "primeiro programa"
    }
)

print("================================")
print(" MORPH-GRAPH CROSS PROGRAM TEST")
print("================================")

print("\n=== PROGRAMA A ===")

engine_a = EvolutionEngine(graph)

result_a = engine_a.evolve(
    "program_a",
    generations=1
)

print(
    "Final A:",
    result_a["final_node"]
)

print("\n=== MEMÓRIA APÓS PROGRAMA A ===")

stats = mutation_statistics(graph)

for item in stats:

    print(
        item["mutation"],
        "|",
        "sucesso=",
        item["success"],
        "|",
        "score=",
        item["score"]
    )

program_b = """
def calcular(x, y):
    return x + y

assert calcular(10, 20) == 30
"""

add_code_node(
    graph,
    "program_b",
    program_b,
    {
        "description": "segundo programa"
    }
)

print("\n=== PROGRAMA B ===")

engine_b = EvolutionEngine(graph)

result_b = engine_b.evolve(
    "program_b",
    generations=1
)

print(
    "Final B:",
    result_b["final_node"]
)

print("\n=== RESULTADO ===")

print(
    "Total de nós:",
    len(graph.nodes)
)

print(
    "Total de conexões:",
    len(graph.edges)
)

print(
    "Histórico:",
    len(graph.history)
)

print("\n=== CÓDIGO FINAL A ===")

print(
    graph.nodes[
        result_a["final_node"]
    ]["data"]["code"]
)

print("\n=== CÓDIGO FINAL B ===")

print(
    graph.nodes[
        result_b["final_node"]
    ]["data"]["code"]
)
