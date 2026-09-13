import ast

from graph.core import Graph
from engine.code_node import add_code_node
from engine.ast_mutation import ASTMutationRule
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
    original_code
)


rules = [

    ASTMutationRule(
        "plus_to_minus",
        "plus_to_minus"
    ),

    ASTMutationRule(
        "swap_operands",
        "swap_operands"
    )
]


engine = EvolutionEngine(graph)

print("================================")
print(" MORPH-GRAPH AST EVOLUTION")
print("================================")

result = engine.evolve(
    "code_001",
    rules,
    generations=3
)


print("\n=== RESULTADO FINAL ===")

final_id = result["final_node"]

print("Nó:", final_id)

print(
    graph.nodes[final_id]["data"]["code"]
)


print("\n=== HISTÓRICO ===")

for item in result["generations"]:

    selected = item["selected"]

    print(
        "Geração",
        item["generation"],
        "|",
        item["source"],
        "->",
        selected["node_id"],
        "| regra:",
        selected["rule"],
        "| score:",
        selected["score"]
    )


print("\n=== NÓS ===")

for node_id, node in graph.nodes.items():

    if node["type"] == "code":

        print(
            node_id,
            "|",
            node["data"].get("generated_by")
        )
