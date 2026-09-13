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

print("ESTADO INICIAL:")
print(graph.snapshot())

print("\nEXECUTANDO STEP:")
result = runner.step()
print(result)

print("\nESTADO APÓS STEP:")
print(graph.snapshot())

print("\nEXECUTANDO SEGUNDO STEP:")
result = runner.step()
print(result)

print("\nESTADO FINAL:")
print(graph.snapshot())
