from graph.core import Graph
from engine.rules import TransformationRule
from engine.evaluator import Evaluation, record_evaluation
from engine.learning import rule_statistics, rank_rules


graph = Graph()

graph.add_node(
    "origin",
    "seed",
    {"message": "primeiro nó"}
)

graph.add_node(
    "node_001",
    "generated",
    {
        "generated_by": "seed_to_generated",
        "source_node": "origin"
    }
)

graph.connect(
    "origin",
    "node_001",
    "seed_to_generated"
)

evaluation = Evaluation(
    True,
    1.0,
    "transformação funcionou"
)

record_evaluation(
    graph,
    "node_001",
    evaluation
)

rules = [
    TransformationRule(
        "seed_to_generated",
        "seed",
        "generated"
    ),
    TransformationRule(
        "seed_to_candidate",
        "seed",
        "candidate"
    )
]

print("=== ESTATÍSTICAS ===")
print(rule_statistics(graph))

print("\n=== RANKING ===")
for item in rank_rules(graph, rules):
    print(item)
