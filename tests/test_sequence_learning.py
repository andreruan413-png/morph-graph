from graph.core import Graph
from engine.sequence_learning import SequenceLearning


def main():
    graph = Graph()

    graph.add_node(
        "problem",
        "problem",
        {"description": "teste de sequência"},
    )

    # Simula decisões que fizeram parte de uma trajetória vencedora.
    graph.add_node(
        "decision_0001",
        "decision",
        {
            "problem_id": "problem",
            "candidate": "A",
            "path": [],
            "useful": True,
            "trajectory_credit": 1.0,
        },
    )

    graph.add_node(
        "decision_0002",
        "decision",
        {
            "problem_id": "problem",
            "candidate": "B",
            "path": ["A"],
            "useful": True,
            "trajectory_credit": 1.0,
        },
    )

    graph.add_node(
        "decision_0003",
        "decision",
        {
            "problem_id": "problem",
            "candidate": "C",
            "path": ["A", "B"],
            "useful": True,
            "trajectory_credit": 1.0,
        },
    )

    # Uma decisão que não recebeu crédito não deve entrar
    # como evidência positiva.
    graph.add_node(
        "decision_0004",
        "decision",
        {
            "problem_id": "problem",
            "candidate": "X",
            "path": ["A", "B"],
            "useful": False,
            "trajectory_credit": -1.0,
        },
    )

    learner = SequenceLearning(graph)

    learned = learner.learn()

    print()
    print("=" * 70)
    print(" MORPH-GRAPH — APRENDIZADO DE SEQUÊNCIA")
    print("=" * 70)

    print()
    print("Sequências aprendidas:")

    for context, candidates in learned.items():
        print(
            "  ",
            list(context),
            "->",
            candidates,
        )

    score_b = learner.score(["A"], "B")
    score_c = learner.score(["A", "B"], "C")
    score_x = learner.score(["A", "B"], "X")

    print()
    print("Score A -> B:", score_b)
    print("Score A,B -> C:", score_c)
    print("Score A,B -> X:", score_x)

    assert score_b > 0.0
    assert score_c > 0.0
    assert score_x == 0.0

    print()
    print("APRENDIZADO DE SEQUENCIA → OK")


if __name__ == "__main__":
    main()
