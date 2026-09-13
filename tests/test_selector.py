from graph.core import Graph
from engine.rules import TransformationRule
from engine.selector import applicable_rules


graph = Graph()

graph.add_node(
    "origin",
    "seed",
    {"message": "primeiro nó"}
)

graph.add_node(
    "other",
    "generated",
    {"message": "outro nó"}
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

matches = applicable_rules(graph, rules)

for match in matches:
    print(match)
