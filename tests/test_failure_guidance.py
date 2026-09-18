from graph.core import Graph
from engine.code_node import add_code_node
from engine.evaluator import Evaluation, record_evaluation
from engine.failure_guidance import FailureGuidance


def main():
    graph = Graph()

    add_code_node(
        graph,
        "source",
        """def resolver(a, b):
    return a + b
""",
        {"role": "source"},
    )

    add_code_node(
        graph,
        "failed_candidate",
        """def resolver(a, b):
    return a * b
""",
        {
            "generated_by": "binop_0_add_to_mult",
            "source_node": "source",
            "region_index": 0,
            "region_type": "BinOp",
        },
    )

    graph.connect(
        "source",
        "failed_candidate",
        "binop_0_add_to_mult",
    )

    evaluation = Evaluation(
        success=False,
        score=0.0,
        reason="testes não passaram",
    )

    record_evaluation(
        graph,
        "failed_candidate",
        evaluation,
    )

    guidance = FailureGuidance(graph)

    print("=== FALHAS APRENDIDAS ===")
    print(
        guidance.rule_failures()
    )

    print()
    print("=== REGIÕES COM FALHA ===")
    print(
        guidance.region_failures()
    )

    class Candidate:
        def __init__(
            self,
            name,
            region_index,
            region_type,
        ):
            self.name = name
            self.region_index = region_index
            self.region_type = region_type

    failed = Candidate(
        "binop_0_add_to_mult",
        0,
        "BinOp",
    )

    unknown = Candidate(
        "binop_0_add_to_sub",
        0,
        "BinOp",
    )

    failed_score = guidance.score_candidate(
        failed
    )

    unknown_score = guidance.score_candidate(
        unknown
    )

    print()
    print("=== DECISÃO ===")
    print(
        "Falha conhecida:",
        failed.name,
        "| score:",
        failed_score,
    )

    print(
        "Transformação desconhecida:",
        unknown.name,
        "| score:",
        unknown_score,
    )

    if failed_score < unknown_score:
        print()
        print(
            "MEMÓRIA DE FALHAS → OK"
        )
        print(
            "FALHA CONHECIDA → PENALIZADA"
        )
    else:
        raise RuntimeError(
            "A falha conhecida não foi penalizada."
        )


if __name__ == "__main__":
    main()
