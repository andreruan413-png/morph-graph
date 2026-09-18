from graph.core import Graph
from engine.decision import DecisionScore
from engine.context_decision_learning import ContextDecisionLearning


graph = Graph()


# ==============================
# EXPERIÊNCIA POSITIVA
# ==============================

graph.add_node(
    "problem_positive",
    "problem",
    {
        "code": """
def solve(a, b):
    return a + b
"""
    },
)

graph.add_node(
    "decision_positive",
    "decision",
    {
        "problem_id": "problem_positive",
        "scores": {
            "context": 100.0,
            "trajectory": 5.0,
            "graph": 1.0,
            "failure": 0.0,
            "transition": 0.0,
            "learned": 0.0,
        },
        "outcome": "success",
    },
)


# ==============================
# EXPERIÊNCIA NEGATIVA
# ==============================

graph.add_node(
    "problem_negative",
    "problem",
    {
        "code": """
def solve(a, b):
    return a - b
"""
    },
)

graph.add_node(
    "decision_negative",
    "decision",
    {
        "problem_id": "problem_negative",
        "scores": {
            "context": 1.0,
            "trajectory": 5.0,
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


print("=== CONTEXTO ===")
print("Código atual: soma")


weights = learning.learned_weights(
    current_code
)


print()
print("=== PESOS APRENDIDOS ===")

for key, value in weights.items():
    print(f"{key}: {value:.4f}")


# Candidato A:
# fortemente apoiado pelo contexto.
candidate_context = DecisionScore.from_values(
    context=100,
    trajectory=5,
    graph=1,
)


# Candidato B:
# fortemente apoiado pelo grafo.
candidate_graph = DecisionScore.from_values(
    context=1,
    trajectory=5,
    graph=100,
)


score_context = learning.score(
    current_code,
    candidate_context,
)

score_graph = learning.score(
    current_code,
    candidate_graph,
)


print()
print("=== RANKING APRENDIDO ===")
print(
    f"Candidato apoiado por CONTEXT: "
    f"{score_context:.4f}"
)
print(
    f"Candidato apoiado por GRAPH: "
    f"{score_graph:.4f}"
)


assert score_context > score_graph


print()
print("CONTEXTO → MUDA RANKING: OK")
print("DECISION LEARNING → RANKING: OK")
print("INTEGRAÇÃO CONTEXTUAL → OK")
