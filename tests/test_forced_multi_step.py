from graph.core import Graph

from engine.code_node import add_code_node

from engine.evolution import EvolutionEngine


graph = Graph()


code = """def calcular(a, b):
    return a - b - 1
"""


tests = """
TEST: assert candidate.calcular(2, 2) == 1
TEST: assert candidate.calcular(3, 2) == 0
TEST: assert candidate.calcular(5, 1) == -3
"""


add_code_node(
    graph,
    "candidate_forced",
    code
)


engine = EvolutionEngine(
    graph,
    tests=tests
)


print()
print("========================================")
print(" MORPH-GRAPH FORCED MULTI-STEP TEST")
print("========================================")

print()
print("=== CÓDIGO INICIAL ===")
print(code)

print()
print("=== OBJETIVO ===")
print("return b - a + 1")

result = engine.evolve(
    "candidate_forced",
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
print("=== TRAJETÓRIA REAL ===")

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

if (
    result["final_score"] >= 1.0
    and len(result["generations"]) >= 2
):

    print(
        "FORCED MULTI-STEP: OK"
    )

elif result["final_score"] >= 1.0:

    print(
        "SOLUÇÃO ENCONTRADA, "
        "MAS EM APENAS UMA ETAPA."
    )

else:

    print(
        "FORCED MULTI-STEP: FALHOU"
    )
