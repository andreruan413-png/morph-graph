from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.path_search import PathSearch
from engine.problem_evaluator import evaluate_problem
from engine.evaluator import Evaluation, record_evaluation


SOURCE = """def resolver(a, b):
    return a + b
"""

TESTS = """TEST: resolver(10, 3) == 7
TEST: resolver(20, 5) == 15
"""


def evaluator(code):
    return evaluate_problem(
        code,
        TESTS
    ).as_dict()


def main():
    graph = Graph()

    graph.add_node(
        "source",
        "code",
        {
            "code": SOURCE,
            "language": "python",
            "role": "source",
        }
    )

    mutator = AutomaticASTMutator()

    # --------------------------------------------------
    # 1. Descobrir os candidatos disponíveis
    # --------------------------------------------------

    candidates = mutator.generate(SOURCE)

    print("=== CANDIDATOS ===")

    for candidate in candidates:
        print(
            candidate.name,
            "| região:",
            candidate.region_index,
            "| tipo:",
            candidate.region_type,
        )

    # --------------------------------------------------
    # 2. Registrar artificialmente uma falha histórica
    # --------------------------------------------------

    failed_candidate = None

    for candidate in candidates:
        if candidate.name == "binop_0_add_to_mult":
            failed_candidate = candidate
            break

    if failed_candidate is None:
        raise RuntimeError(
            "Candidato binop_0_add_to_mult não encontrado."
        )

    failed_code = failed_candidate.code()

    failed_node = graph.add_node(
        "historical_failure",
        "code",
        {
            "code": failed_code,
            "language": "python",
            "generated_by": failed_candidate.name,
            "source_node": "source",
            "region_index": failed_candidate.region_index,
            "region_type": failed_candidate.region_type,
        }
    )

    graph.connect(
        "source",
        "historical_failure",
        failed_candidate.name
    )

    record_evaluation(
        graph,
        failed_node["id"],
        Evaluation(
            success=False,
            score=0.0,
            reason="falha histórica conhecida"
        )
    )

    print()
    print("=== FALHA HISTÓRICA ===")
    print(
        failed_candidate.name,
        "| score de falha esperado: negativo"
    )

    # --------------------------------------------------
    # 3. Criar PathSearch com FailureGuidance
    # --------------------------------------------------

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=1,
        beam_width=10,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        transition_memory=None,
        use_graph_guidance=False,
        use_context_guidance=False,
        use_failure_guidance=True,
    )

    # --------------------------------------------------
    # 4. Executar busca
    # --------------------------------------------------

    result = search.search("source")

    print()
    print("=== RESULTADO DA BUSCA ===")
    print("Sucesso:", result["success"])
    print("Caminho:", result["path"])

    # --------------------------------------------------
    # 5. Verificar se a falha realmente influenciou
    # --------------------------------------------------

    from engine.failure_guidance import FailureGuidance

    guidance = FailureGuidance(graph)

    ranking = guidance.rank(candidates)

    print()
    print("=== RANKING DA MEMÓRIA DE FALHAS ===")

    for item in ranking:
        print(
            item["name"],
            "| failure_score:",
            item["failure_score"]
        )

    failed_score = guidance.score_candidate(
        failed_candidate
    )

    unknown_candidate = None

    for candidate in candidates:
        if candidate.name != failed_candidate.name:
            unknown_candidate = candidate
            break

    unknown_score = guidance.score_candidate(
        unknown_candidate
    )

    print()
    print("=== VERIFICAÇÃO ===")
    print(
        "Falha conhecida:",
        failed_candidate.name,
        "| score:",
        failed_score
    )
    print(
        "Candidato desconhecido:",
        unknown_candidate.name,
        "| score:",
        unknown_score
    )

    if failed_score >= unknown_score:
        raise AssertionError(
            "A falha conhecida não foi penalizada."
        )

    print()
    print("FAILURE GUIDANCE → MUDOU A PRIORIDADE: OK")
    print("PATHSEARCH → FAILURE GUIDANCE: OK")
    print("MEMÓRIA NEGATIVA → DECISÃO: OK")


if __name__ == "__main__":
    main()
