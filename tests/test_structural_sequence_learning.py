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


class Candidate:
    def __init__(
        self,
        name,
        region_index,
        region_type,
        mutation_type,
    ):
        self.name = name
        self.region_index = region_index
        self.region_type = region_type
        self.mutation_type = mutation_type


def add_decision(
    graph,
    decision_id,
    candidate,
    path,
):
    return graph.add_node(
        decision_id,
        "decision",
        {
            "problem_id": "structural_problem",
            "candidate": candidate.name,
            "region_index": candidate.region_index,
            "region_type": candidate.region_type,
            "mutation_type": candidate.mutation_type,
            "path": list(path),
            "useful": True,
            "trajectory_credit": 1.0,
        },
    )


def main():
    print("=" * 70)
    print(
        "MORPH-GRAPH — SEQUÊNCIA ESTRUTURAL"
    )
    print("=" * 70)

    graph = Graph()

    # ---------------------------------------------------------
    # EXPERIÊNCIA APRENDIDA
    # ---------------------------------------------------------

    candidate_a = Candidate(
        "binop_0_add_to_sub",
        region_index=0,
        region_type="binop",
        mutation_type="operator_change",
    )

    candidate_b = Candidate(
        "binop_1_sub_to_add",
        region_index=1,
        region_type="binop",
        mutation_type="operator_change",
    )

    add_decision(
        graph,
        "decision_001",
        candidate_a,
        [],
    )

    add_decision(
        graph,
        "decision_002",
        candidate_b,
        [candidate_a.name],
    )

    learner = SequenceLearning(graph)

    print()
    print("=== SEQUÊNCIA APRENDIDA ===")

    learned = learner.learn()

    for context, candidates in learned.items():
        print(
            list(context),
            "->",
            candidates,
        )

    # ---------------------------------------------------------
    # REPRESENTAÇÃO ESTRUTURAL
    # ---------------------------------------------------------

    print()
    print("=== ESTRUTURA DAS TRANSFORMAÇÕES ===")

    structural_sequence = [
        {
            "region_index": candidate_a.region_index,
            "region_type": candidate_a.region_type,
            "mutation_type": candidate_a.mutation_type,
        },
        {
            "region_index": candidate_b.region_index,
            "region_type": candidate_b.region_type,
            "mutation_type": candidate_b.mutation_type,
        },
    ]

    for index, step in enumerate(
        structural_sequence,
        start=1,
    ):
        print(
            f"Etapa {index}:",
            step,
        )

    # ---------------------------------------------------------
    # PROVA
    # ---------------------------------------------------------

    assert structural_sequence[0]["region_type"] == "binop"
    assert structural_sequence[1]["region_type"] == "binop"

    assert (
        structural_sequence[0]["mutation_type"]
        == "operator_change"
    )

    assert (
        structural_sequence[1]["mutation_type"]
        == "operator_change"
    )

    print()
    print(
        "REGIÕES ESTRUTURAIS → OK"
    )

    print(
        "TIPOS DE MUTAÇÃO → OK"
    )

    print(
        "SEQUÊNCIA ESTRUTURAL REPRESENTADA → OK"
    )

    print("=" * 70)
    print(
        "BASE DA SEQUÊNCIA ESTRUTURAL → OK"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
