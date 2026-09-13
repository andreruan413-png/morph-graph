from graph.core import Graph
from engine.rules import TransformationRule
from engine.runner import MorphRunner


graph = Graph()

graph.add_node(
    "origin",
    "seed",
    {"message": "primeiro nó"}
)

rules = [
    TransformationRule(
        "seed_to_generated",
        "seed",
        "generated"
    ),
    TransformationRule(
        "generated_to_candidate",
        "generated",
        "candidate"
    )
]

runner = MorphRunner(graph, rules)

print("MOVIMENTOS POSSÍVEIS:")
for move in runner.find_moves():
    print(move)

print("\nEXECUTANDO PRIMEIRO MOVIMENTO:")

runner.run(
    "origin",
    "seed_to_generated",
    "node_001",
    {"message": "resultado criado pelo motor"}
)

print("\nNOVO ESTADO:")
print(graph.snapshot())
