import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from graph.core import Graph
from engine.sequence_learning import SequenceLearning


def add_decision(
    graph,
    decision_id,
    candidate,
    region_index,
    region_type,
    mutation_type,
    path,
):
    return graph.add_node(
        decision_id,
        "decision",
        {
            "problem_id": "structural_transfer_problem",
            "candidate": candidate,
            "region_index": region_index,
            "region_type": region_type,
            "mutation_type": mutation_type,
            "path": list(path),
            "useful": True,
            "trajectory_credit": 1.0,
        },
    )


def main():
    print("=" * 70)
    print("MORPH-GRAPH — TRANSFERÊNCIA ESTRUTURAL")
    print("=" * 70)

    graph = Graph()

    # =========================================================
    # EXPERIÊNCIA APRENDIDA
    #
    # O sistema aprendeu uma sequência usando estes nomes:
    #
    # old_add
    # old_sub
    #
    # =========================================================

    add_decision(
        graph,
        "decision_old_1",
        "old_add",
        region_index=0,
        region_type="binop",
        mutation_type="operator_change",
        path=[],
    )

    add_decision(
        graph,
        "decision_old_2",
        "old_sub",
        region_index=1,
        region_type="binop",
        mutation_type="operator_change",
        path=["old_add"],
    )

    learner = SequenceLearning(graph)

    print()
    print("=== EXPERIÊNCIA ORIGINAL ===")

    for context, candidates in learner.learn().items():
        print(
            list(context),
            "->",
            candidates,
        )

    # =========================================================
    # NOVA EXPERIÊNCIA
    #
    # Os nomes agora são completamente diferentes:
    #
    # new_mul
    # new_div
    #
    # Mas a estrutura da transformação é a mesma.
    #
    # =========================================================

    add_decision(
        graph,
        "decision_new_1",
        "new_mul",
        region_index=0,
        region_type="binop",
        mutation_type="operator_change",
        path=[],
    )

    add_decision(
        graph,
        "decision_new_2",
        "new_div",
        region_index=1,
        region_type="binop",
        mutation_type="operator_change",
        path=["new_mul"],
    )

    print()
    print("=== NOVA EXPERIÊNCIA ===")

    structural = learner.structural_learn()

    for context, candidates in structural.items():
        print(
            list(context),
            "->",
            candidates,
        )

    # =========================================================
    # TRANSFERÊNCIA
    #
    # O novo candidato new_div possui exatamente a mesma
    # assinatura estrutural que old_sub.
    #
    # =========================================================

    old_sub_signature = (
        1,
        "binop",
        "operator_change",
    )

    new_div_signature = (
        1,
        "binop",
        "operator_change",
    )

    similarity = learner.structural_similarity(
        old_sub_signature,
        new_div_signature,
    )

    print()
    print("=== SIMILARIDADE ENTRE TRANSFORMAÇÕES ===")

    print(
        "old_sub:",
        old_sub_signature,
    )

    print(
        "new_div:",
        new_div_signature,
    )

    print(
        "Similaridade:",
        similarity,
    )

    assert similarity == 1.0

    # =========================================================
    # PROVA DE TRANSFERÊNCIA
    # =========================================================

    score = learner.score_structural(
        [
            (
                0,
                "binop",
                "operator_change",
            )
        ],
        new_div_signature,
    )

    print()
    print(
        "Score estrutural transferido:",
        score,
    )

    assert score > 0.0, (
        "ERRO: nenhuma evidência estrutural "
        "foi transferida."
    )

    print()
    print(
        "MESMA ESTRUTURA → OK"
    )

    print(
        "NOMES DIFERENTES → OK"
    )

    print(
        "TRANSFERÊNCIA ESTRUTURAL → OK"
    )

    print("=" * 70)
    print(
        "TRANSFERÊNCIA ENTRE MUTAÇÕES → OK"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
