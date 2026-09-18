from graph.core import Graph
from engine.decision import DecisionScore
from engine.decision_learning import DecisionLearning


graph = Graph()

graph.add_node(
    "problem_001",
    "problem",
    {"description": "teste"}
)

graph.add_node(
    "decision_001",
    "decision",
    {
        "scores": {
            "context": 100.0,
            "trajectory": 20.0,
            "graph": 5.0,
            "failure": 0.0,
            "transition": 2.0,
            "learned": 1.0,
            "total": 128.0,
        },
        "outcome": "success",
    }
)

graph.add_node(
    "decision_002",
    "decision",
    {
        "scores": {
            "context": 20.0,
            "trajectory": 5.0,
            "graph": 2.0,
            "failure": 0.0,
            "transition": 1.0,
            "learned": 0.0,
            "total": 28.0,
        },
        "outcome": "failure",
    }
)

learning = DecisionLearning(graph)

weights = learning.learned_weights()

print("=== PESOS APRENDIDOS ===")

for key, value in weights.items():
    print(f"{key}: {value:.2f}")

score = DecisionScore.from_values(
    context=100.0,
    trajectory=20.0,
    graph=5.0,
    failure=0.0,
    transition=2.0,
    learned=1.0,
)

learned_score = learning.score(score)

print()
print("=== NOVA DECISÃO ===")
print(f"Score aprendido: {learned_score:.2f}")

explanation = learning.explain(score)

print()
print("=== CONTRIBUIÇÕES ===")

for key, data in explanation.items():
    print(
        f"{key}: "
        f"valor={data['normalized_value']:.2f} "
        f"peso={data['weight']:.2f} "
        f"contribuição={data['contribution']:.2f}"
    )

print()
print("DECISION LEARNING → OK")
