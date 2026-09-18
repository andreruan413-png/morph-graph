import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from graph.core import Graph
from engine.decision import DecisionScore
from engine.context_decision_learning import ContextDecisionLearning


CODE = """
def resolver(a, b):
    return (a + b, a - b)
"""


def add_decision(
    graph,
    decision_id,
    candidate,
    outcome,
    scores,
):
    graph.add_node(
        decision_id,
        "decision",
        {
            "candidate": candidate,
            "outcome": outcome,
            "scores": scores,
            "source_code": CODE,
        },
    )


def main():
    print("=" * 70)
    print(" MORPH-GRAPH — ESCOLHA APRENDIDA ENTRE CANDIDATOS")
    print("=" * 70)

    # ---------------------------------------------------------
    # GRAFO FRESCO
    # ---------------------------------------------------------

    fresh_graph = Graph()
    learner_fresh = ContextDecisionLearning(fresh_graph)

    candidate_a = DecisionScore(
        context=100.0,
        trajectory=0.0,
        graph=0.0,
        failure=0.0,
        transition=0.0,
        learned=0.0,
    )

    candidate_b = DecisionScore(
        context=0.0,
        trajectory=0.0,
        graph=100.0,
        failure=0.0,
        transition=0.0,
        learned=0.0,
    )

    fresh_a = learner_fresh.score(CODE, candidate_a)
    fresh_b = learner_fresh.score(CODE, candidate_b)

    print()
    print("=== SEM HISTÓRICO ===")
    print("Candidato A:", fresh_a)
    print("Candidato B:", fresh_b)

    # Sem conhecimento, os dois devem começar iguais.
    assert fresh_a == 0.0
    assert fresh_b == 0.0

    # ---------------------------------------------------------
    # HISTÓRICO
    #
    # A → contexto forte → sucesso
    # B → graph forte    → falha
    # ---------------------------------------------------------

    learned_graph = Graph()

    add_decision(
        learned_graph,
        "decision_success_context",
        "candidate_A",
        "success",
        {
            "context": 100.0,
            "trajectory": 0.0,
            "graph": 0.0,
            "failure": 0.0,
            "transition": 0.0,
            "learned": 0.0,
            "total": 100.0,
        },
    )

    add_decision(
        learned_graph,
        "decision_failure_graph",
        "candidate_B",
        "failure",
        {
            "context": 0.0,
            "trajectory": 0.0,
            "graph": 100.0,
            "failure": 0.0,
            "transition": 0.0,
            "learned": 0.0,
            "total": 100.0,
        },
    )

    learner = ContextDecisionLearning(learned_graph)

    print()
    print("=== PESOS APRENDIDOS ===")

    weights = learner.learned_weights(CODE)

    for key, value in weights.items():
        print(f"{key}: {value:.4f}")

    learned_a = learner.score(CODE, candidate_a)
    learned_b = learner.score(CODE, candidate_b)

    print()
    print("=== APÓS O APRENDIZADO ===")
    print("Candidato A:", learned_a)
    print("Candidato B:", learned_b)

    print()
    print("=== COMPARAÇÃO ===")

    if learned_a > learned_b:
        print("ESCOLHA APRENDIDA: CANDIDATO A")
    elif learned_b > learned_a:
        print("ESCOLHA APRENDIDA: CANDIDATO B")
    else:
        print("EMPATE")

    # O histórico deve ensinar:
    # contexto → evidência positiva
    # graph    → evidência negativa
    assert weights["context"] > 0.0
    assert weights["graph"] < 0.0

    # Portanto A deve superar B.
    assert learned_a > learned_b

    print()
    print("CONTEXTO → APRENDEU: OK")
    print("GRAPH → APRENDEU NEGATIVAMENTE: OK")
    print("RANKING → CANDIDATO A > CANDIDATO B: OK")
    print()
    print("LEARNED CHOICE → OK")


if __name__ == "__main__":
    main()
