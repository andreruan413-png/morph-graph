from graph.core import Graph
from engine.rules import TransformationRule
from engine.runner import MorphRunner
from engine.evaluator import evaluate_node, record_evaluation


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

print("=== STEP 1 ===")

result = runner.step()

print(result)

node = graph.nodes[result["created"]]

evaluation = evaluate_node(
    node,
    "generated"
)

evaluation_id = record_evaluation(
    graph,
    result["created"],
    evaluation
)

print("\n=== AVALIAÇÃO ===")
print(evaluation.as_dict())

print("\n=== NÓ DA AVALIAÇÃO ===")
print(graph.nodes[evaluation_id])

print("\n=== CONEXÕES ===")

for edge in graph.edges:
    print(edge)

print("\n=== HISTÓRICO ===")

for item in graph.history:
    print(item)
