from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine


graph = Graph()


source = """
def calcular(a, b):
    return a - b
"""


tests = """
import sys
import importlib.util

candidate_path = sys.argv[1]

spec = importlib.util.spec_from_file_location(
    "candidate",
    candidate_path
)

candidate = importlib.util.module_from_spec(spec)

spec.loader.exec_module(candidate)


assert candidate.calcular(10, 3) == 13
assert candidate.calcular(20, 5) == 25
assert candidate.calcular(7, 2) == 9

print("TODOS OS TESTES PASSARAM")
"""


add_code_node(
    graph,
    "problem_001",
    source,
    {
        "description": "calcular soma",
        "problem_type": "programming_problem"
    }
)


print("================================")
print(" MORPH-GRAPH REAL PROBLEM")
print("================================")

print("\nOBJETIVO:")
print("calcular(a, b) deve retornar a + b")

engine = EvolutionEngine(
    graph,
    tests=tests
)


result = engine.evolve(
    "problem_001",
    generations=5
)


print("\n=== RESULTADO FINAL ===")

final_id = result["final_node"]

print("Nó:", final_id)

print(
    graph.nodes[
        final_id
    ]["data"]["code"]
)

print("\n=== CAMINHO ===")

for item in result["generations"]:

    selected = item["selected"]

    print(
        f"Geração {item['generation']} | "
        f"{selected['rule']} | "
        f"score={selected['score']} | "
        f"success={selected['success']}"
    )

print("\n=== GRAFO ===")

print("Nós:", len(graph.nodes))
print("Conexões:", len(graph.edges))
print("Histórico:", len(graph.history))
