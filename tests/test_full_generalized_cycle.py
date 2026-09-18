import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from graph.core import Graph
from engine.path_search import PathSearch
from engine.sequence_learning import SequenceLearning


class Candidate:
    def __init__(self, name, region_index):
        self.name = name
        self.region_index = region_index
        self.region_type = "binop"


class NeutralMutator:
    def generate(self, code):
        return []


def neutral_evaluator(code):
    return {
        "success": False,
        "score": 0.0,
    }


def make_search(graph):
    return PathSearch(
        graph=graph,
        mutator=NeutralMutator(),
        evaluator=neutral_evaluator,
        max_depth=1,
        beam_width=2,
        use_trajectory=False,
        use_structure=False,
        use_graph_guidance=False,
        use_context_guidance=False,
        use_failure_guidance=False,
        use_decision_score=True,
    )


def add_useful_decision(
    graph,
    decision_id,
    candidate,
    path,
):
    node = graph.add_node(
        decision_id,
        "decision",
        {
            "problem_id": "experience_problem",
            "candidate": candidate,
            "region_index": 0,
            "region_type": "binop",
            "path": list(path),
            "useful": True,
            "trajectory_credit": 1.0,
            "scores": {
                "sequence_learning": 0.0,
            },
        },
    )

    return node


def main():
    print("=" * 70)
    print("MORPH-GRAPH — CICLO COMPLETO DE GENERALIZAÇÃO")
    print("=" * 70)

    graph = Graph()

    graph.add_node(
        "program",
        "code",
        {
            "code": "def resolver(a, b): return a + b",
            "language": "python",
        },
    )

    # ---------------------------------------------------------
    # EXPERIÊNCIA 1
    # ---------------------------------------------------------

    print()
    print("=== EXPERIÊNCIA 1 ===")

    add_useful_decision(
        graph,
        "decision_exp1_a",
        "A",
        [],
    )

    add_useful_decision(
        graph,
        "decision_exp1_b",
        "B",
        ["A"],
    )

    # ---------------------------------------------------------
    # EXPERIÊNCIA 2
    # Mesmo mecanismo, mas contexto diferente.
    # ---------------------------------------------------------

    print()
    print("=== EXPERIÊNCIA 2 ===")

    add_useful_decision(
        graph,
        "decision_exp2_a",
        "A",
        ["X"],
    )

    add_useful_decision(
        graph,
        "decision_exp2_b",
        "B",
        ["X", "A"],
    )

    learner = SequenceLearning(graph)

    print()
    print("=== EXPERIÊNCIAS APRENDIDAS ===")

    learned = learner.learn()

    for context, candidates in learned.items():
        print(
            list(context),
            "->",
            candidates,
        )

    # ---------------------------------------------------------
    # NOVO CONTEXTO
    #
    # [X,Y] é diferente dos contextos armazenados.
    # Porém possui estrutura parcialmente semelhante.
    # ---------------------------------------------------------

    current_path = ["A", "Y"]

    candidate_a = Candidate(
        "A",
        region_index=1,
    )

    candidate_b = Candidate(
        "B",
        region_index=0,
    )

    print()
    print("=== REUTILIZAÇÃO GENERALIZADA ===")

    score_a = learner.score(
        current_path,
        candidate_a.name,
    )

    score_b = learner.score(
        current_path,
        candidate_b.name,
    )

    print(
        "Contexto atual:",
        current_path,
    )

    print(
        "Score A:",
        score_a,
    )

    print(
        "Score B:",
        score_b,
    )

    assert score_b > 0.0, (
        "ERRO: nenhuma evidência generalizada foi transferida para B."
    )

    # ---------------------------------------------------------
    # PATHSEARCH REAL
    # ---------------------------------------------------------

    print()
    print("=== PATHSEARCH ===")

    search = make_search(graph)

    search._current_code = (
        "def resolver(a, b): return a + b"
    )

    without_generalization = (
        search._candidate_sort_key(
            current_path,
            candidate_a,
        ),
        search._candidate_sort_key(
            current_path,
            candidate_b,
        ),
    )

    print()
    print("Scores com SequenceLearning generalizado:")

    print(
        "A:",
        search._decision_score_for_candidate(
            current_path,
            candidate_a,
        ).as_dict(),
    )

    print(
        "B:",
        search._decision_score_for_candidate(
            current_path,
            candidate_b,
        ).as_dict(),
    )

    ranked = sorted(
        [candidate_a, candidate_b],
        key=lambda candidate: search._candidate_sort_key(
            current_path,
            candidate,
        ),
        reverse=True,
    )

    order = [
        candidate.name
        for candidate in ranked
    ]

    print()
    print(
        "Ordem final do PathSearch:",
        order,
    )

    assert order[0] == "B", (
        "ERRO: a evidência generalizada não alterou "
        "a decisão do PathSearch."
    )

    decision_score_b = (
        search._decision_score_for_candidate(
            current_path,
            candidate_b,
        )
    )

    assert (
        decision_score_b.sequence_learning > 0.0
    ), (
        "ERRO: sequence_learning não entrou "
        "no DecisionScore."
    )

    print()
    print(
        "EVIDÊNCIA DAS EXPERIÊNCIAS → OK"
    )

    print(
        "GENERALIZAÇÃO ENTRE CONTEXTOS → OK"
    )

    print(
        "GENERALIZAÇÃO NO PATHSEARCH → OK"
    )

    print(
        "SEQUENCE LEARNING NO DECISION SCORE → OK"
    )

    print("=" * 70)
    print(
        "CICLO COMPLETO DE GENERALIZAÇÃO → OK"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
