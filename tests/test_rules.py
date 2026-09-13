from graph.core import Graph
from engine.rules import TransformationRule


graph = Graph()

graph.add_node(
    "origin",
    "seed",
    {"message": "primeiro nó"}
)

rule = TransformationRule(
    "seed_to_generated",
    "seed",
    "generated"
)

rule.transform(
    graph,
    "origin",
    "node_001",
    {"message": "resultado da transformação"}
)

print(graph.snapshot())
