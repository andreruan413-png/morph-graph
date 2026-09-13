from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine


graph = Graph()

code = """
def soma(a, b):
    return a + b

assert soma(2, 3) == 5
"""

add_code_node(
    graph,
    "code_001",
    code,
    {
        "description": "programa inicial"
    }
)

engine = EvolutionEngine(graph)

print("================================")
print(" MORPH-GRAPH INTEGRATED ENGINE")
print("================================")

result = engine.evolve(
    "code_001",
    generations=5
)

print("\n=== RESULTADO FINAL ===")

final_id = result["final_node"]

print("Nó:", final_id)

print(
    graph.nodes[final_id]["data"]["code"]
)

print("\n=== CAMINHO ===")

for item in result["generations"]:

    print(
        f"Geração {item['generation']} | "
        f"{item['source']} -> "
        f"{item['selected']['node_id']} | "
        f"{item['selected']['rule']} | "
        f"score={item['selected']['score']}"
    )

print("\n=== GRAFO ===")

print(
    "Nós:",
    len(graph.nodes)
)

print(
    "Conexões:",
    len(graph.edges)
)
