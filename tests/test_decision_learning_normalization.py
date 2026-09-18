from graph.core import Graph
from engine.decision import DecisionScore
from engine.decision_learning import DecisionLearning


graph = Graph()

graph.add_node(
    "decision_success",
    "decision",
    {
        "scores": {
            "context": 1000.0,
            "trajectory": 10.0,
            "graph": 1.0,
            "failure": 0.0,
            "transition": 0.0,
            "learned": 0.0,
        },
        "outcome": "success",
    }
)

graph.add_node(
    "decision_failure",
    "decision",
    {
        "scores": {
            "context": 1.0,
            "trajectory": 10.0,
            "graph": 1000.0,
            "failure": 0.0,
            "transition": 0.0,
            "learned": 0.0,
        },
        "outcome": "failure",
    }
)

learning = DecisionLearning(graph)

print("=== PESOS ===")

weights = learning.learned_weights()

for key, value in weights.items():
    print(f"{key}: {value:.4f}")

print()
print("=== CONFIABILIDADE ===")

for key, data in learning.reliability().items():
    print(
        f"{key}: "
        f"observações={data['observations']:.2f} "
        f"taxa_sucesso={data['success_rate']:.4f} "
        f"peso={data['weight']:.4f}"
    )

positive = DecisionScore.from_values(
    context=1000,
    trajectory=10,
    graph=1,
)

negative = DecisionScore.from_values(
    context=1,
    trajectory=10,
    graph=1000,
)

positive_score = learning.score(positive)
negative_score = learning.score(negative)

print()
print("=== COMPARAÇÃO ===")
print(f"Decisão positiva: {positive_score:.4f}")
print(f"Decisão negativa: {negative_score:.4f}")

assert positive_score > negative_score

print()
print("NORMALIZAÇÃO → OK")
print("DECISION LEARNING → OK")
