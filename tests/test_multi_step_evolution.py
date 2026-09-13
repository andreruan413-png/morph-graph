from graph.core import Graph

from engine.code_node import add_code_node

from engine.evolution import EvolutionEngine


graph = Graph()


code = """def calcular(a, b):
    return a - b - 1
"""


tests = """
TEST: assert candidate.calcular(10, 3) == 8
TEST: assert candidate.calcular(20, 5) == 16
TEST: assert candidate.calcular(7, 2) == 6
"""


add_code_node(
    graph,
    "candidate_multi",
    code
)


engine = EvolutionEngine(
    graph,
    tests=tests
)


print()
print("================================")
print(" MORPH-GRAPH MULTI-STEP TEST")
print("================================")

print()
print("=== CÓDIGO INICIAL ===")
print(code)

result = engine.evolve(
    "candidate_multi",
    generations=5
)

print()
print("=== RESULTADO ===")

print(
    "Nó final:",
    result["final_node"]
)

print(
    "Score final:",
    result["final_score"]
)

print(
    "Gerações utilizadas:",
    len(result["generations"])
)

print()
print("=== TRAJETÓRIA ===")

for generation in result["generations"]:

    selected = generation["selected"]

    print(
        f"Geração {generation['generation']}: "
        f"{selected['rule']} "
        f"score={selected['score']}"
    )

print()
print("=== CÓDIGO FINAL ===")

final_node = graph.nodes[
    result["final_node"]
]

print(
    final_node["data"]["code"]
)

print()
print("=== VERIFICAÇÃO ===")

if result["final_score"] >= 1.0:

    print(
        "MULTI-STEP EVOLUTION: OK"
    )

else:

    print(
        "MULTI-STEP EVOLUTION: FALHOU"
    )
