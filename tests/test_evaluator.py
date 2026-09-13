from graph.core import Graph
from engine.rules import TransformationRule
from engine.runner import MorphRunner
from engine.evaluator import evaluate_node


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

result = runner.step()

node = graph.nodes[result["created"]]

evaluation = evaluate_node(
    node,
    "generated"
)

print("TRANSFORMAÇÃO:")
print(result)

print("\nRESULTADO:")
print(node)

print("\nAVALIAÇÃO:")
print(evaluation.as_dict())
