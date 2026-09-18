from graph.core import Graph
from engine.decision import DecisionScore
from engine.context_decision_learning import ContextDecisionLearning


graph = Graph()


# Contexto A:
# context foi associado a sucesso.
graph.add_node(
    "problem_a",
    "problem",
    {
        "code": """
def solve(a, b):
    return a + b
"""
    },
)

graph.add_node(
    "decision_a",
    "decision",
    {
        "problem_id": "problem_a",
        "scores": {
            "context": 100.0,
            "trajectory": 10.0,
            "graph": 1.0,
            "failure": 0.0,
            "transition": 0.0,
            "learned": 0.0,
        },
        "outcome": "success",
    },
)


# Contexto B:
# graph foi associado a falha.
graph.add_node(
    "problem_b",
    "problem",
    {
        "code": """
def solve(a, b):
    return a - b
"""
    },
)

graph.add_node(
    "decision_b",
    "decision",
    {
        "problem_id": "problem_b",
        "scores": {
            "context": 1.0,
            "trajectory": 10.0,
            "graph": 100.0,
            "failure": 0.0,
            "transition": 0.0,
            "learned": 0.0,
        },
        "outcome": "failure",
    },
)


learning = ContextDecisionLearning(
    graph,
    similarity_threshold=0.5,
)


current_code = """
def solve(a, b):
    return a + b
"""


print("=== PESOS DO CONTEXTO ATUAL ===")

weights = learning.learned_weights(
    current_code
)

for key, value in weights.items():
    print(f"{key}: {value:.4f}")


decision = DecisionScore.from_values(
    context=100,
    trajectory=10,
    graph=1,
)


score = learning.score(
    current_code,
    decision,
)


print()
print("=== SCORE CONTEXTUAL ===")
print(f"Score: {score:.4f}")


print()
print("=== EXPLICAÇÃO ===")

for key, data in learning.explain(
    current_code,
    decision,
).items():
    print(
        f"{key}: "
        f"valor={data['normalized_value']:.4f} "
        f"peso={data['weight']:.4f} "
        f"contribuição={data['contribution']:.4f}"
    )


assert weights["context"] > 0
assert weights["graph"] <= 0
assert score > 0


print()
print("CONTEXTO → PESOS ESPECÍFICOS: OK")
print("DECISION LEARNING CONTEXTUAL → OK")
