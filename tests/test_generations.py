from graph.core import Graph
from engine.code_node import add_code_node
from engine.code_mutation import CodeMutationRule
from engine.evolution import EvolutionEngine


graph = Graph()

original_code = """
def soma(a, b):
    return a + b

assert soma(2, 3) == 5
"""

add_code_node(
    graph,
    "code_001",
    original_code,
    {
        "description": "programa inicial"
    }
)


rules = [

    CodeMutationRule(
        "change_plus_to_minus",
        "return a + b",
        "return a - b"
    ),

    CodeMutationRule(
        "change_plus_to_sum",
        "return a + b",
        "return b + a"
    )
]


engine = EvolutionEngine(graph)


print("================================")
print("   MORPH-GRAPH EVOLUTION TEST")
print("================================")

result = engine.evolve(
    "code_001",
    rules,
    generations=3
)


print("\n=== RESULTADO FINAL ===")

print(
    "Nó final:",
    result["final_node"]
)


print("\n=== HISTÓRICO DE EVOLUÇÃO ===")

for generation in result["generations"]:

    print(
        f"Geração {generation['generation']}: "
        f"{generation['source']} "
        f"-> "
        f"{generation['selected']['node_id']} "
        f"usando "
        f"{generation['selected']['rule']} "
        f"(score "
        f"{generation['selected']['score']})"
    )


print("\n=== TOTAL DE NÓS ===")
print(len(graph.nodes))

print("\n=== TOTAL DE CONEXÕES ===")
print(len(graph.edges))
