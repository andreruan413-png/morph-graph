from graph.core import Graph
from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.experience import ExperienceRecorder
from engine.context_guidance import ContextGuidance


TRAIN_A_SOURCE = """def resolver(a, b):
    return a + b
"""

TRAIN_A_TESTS = """TEST: resolver(10, 3) == 7
TEST: resolver(20, 5) == 15
"""


TRAIN_B_SOURCE = """def resolver(a, b):
    c = a + b
    return c
"""

TRAIN_B_TESTS = """TEST: resolver(10, 3) == 7
TEST: resolver(20, 5) == 15
"""


TRAIN_C_SOURCE = """def resolver(a, b):
    return a * b
"""

TRAIN_C_TESTS = """TEST: resolver(10, 3) == 13
TEST: resolver(20, 5) == 25
"""


NEW_SOURCE = """def resolver(x, y):
    return x + y
"""

NEW_TESTS = """TEST: resolver(100, 37) == 63
TEST: resolver(50, 12) == 38
"""


def search_problem(graph, source_id, tests):
    mutator = AutomaticASTMutator()

    def evaluator(code):
        return evaluate_problem(
            code,
            tests
        ).as_dict()

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        use_context_guidance=False,
    )

    return search.search(source_id)


def train(
    graph,
    problem_id,
    source_id,
    source_code,
    tests,
):
    graph.add_node(
        problem_id,
        "problem",
        {
            "description": problem_id,
            "language": "python",
        },
    )

    add_code_node(
        graph,
        source_id,
        source_code,
        {
            "role": "source",
        },
    )

    graph.connect(
        problem_id,
        source_id,
        "has_candidate",
    )

    result = search_problem(
        graph,
        source_id,
        tests,
    )

    if not result.get("success"):
        raise RuntimeError(
            f"Treinamento {problem_id} falhou: "
            f"{result}"
        )

    recorder = ExperienceRecorder(graph)

    experience_id = recorder.record_solution(
        problem_id,
        result,
    )

    if not experience_id:
        raise RuntimeError(
            f"Experiência {problem_id} não registrada."
        )

    return result, experience_id


def main():
    graph = Graph()

    print("=== TREINAMENTO A ===")

    result_a, exp_a = train(
        graph,
        "problem_a",
        "source_a",
        TRAIN_A_SOURCE,
        TRAIN_A_TESTS,
    )

    print("Caminho A:", result_a.get("path"))
    print("Experiência A:", exp_a)

    print()
    print("=== TREINAMENTO B ===")

    result_b, exp_b = train(
        graph,
        "problem_b",
        "source_b",
        TRAIN_B_SOURCE,
        TRAIN_B_TESTS,
    )

    print("Caminho B:", result_b.get("path"))
    print("Experiência B:", exp_b)

    print()
    print("=== TREINAMENTO C — DISTRATOR ===")

    result_c, exp_c = train(
        graph,
        "problem_c",
        "source_c",
        TRAIN_C_SOURCE,
        TRAIN_C_TESTS,
    )

    print("Caminho C:", result_c.get("path"))
    print("Experiência C:", exp_c)

    print()
    print("=== EXPERIÊNCIAS RECUPERADAS ===")

    guidance = ContextGuidance(graph)

    experiences = guidance.rank_experiences(
        NEW_SOURCE
    )

    for experience in experiences:
        print(
            experience["experience_id"],
            "| similaridade:",
            round(
                experience["similarity"],
                6
            ),
            "| score:",
            experience["score"],
        )

    if len(experiences) < 3:
        raise RuntimeError(
            "As três experiências não foram recuperadas."
        )

    print()
    print("=== RANKING DAS TRANSFORMAÇÕES ===")

    mutator = AutomaticASTMutator()

    candidates = mutator.generate(
        NEW_SOURCE
    )

    ranked = guidance.rank(
        NEW_SOURCE,
        candidates,
        [],
    )

    for item in ranked:
        print(
            item["name"],
            "| context_score:",
            round(
                item["context_score"],
                6
            ),
            "| região:",
            item["candidate"].region_index,
        )

    if not ranked:
        raise RuntimeError(
            "Nenhum candidato foi gerado."
        )

    best = ranked[0]

    print()
    print(
        "PRIMEIRO CANDIDATO:",
        best["name"],
    )

    if best["name"] != "binop_0_add_to_sub":
        raise RuntimeError(
            "A combinação das experiências "
            "não priorizou add_to_sub."
        )

    # Mede a evidência acumulada pelas experiências
    # que recomendam a mesma transformação.
    add_to_sub_score = next(
        item["context_score"]
        for item in ranked
        if item["name"] == "binop_0_add_to_sub"
    )

    if add_to_sub_score <= 150.0:
        raise RuntimeError(
            "A evidência das múltiplas experiências "
            "não foi acumulada."
        )

    print(
        "MÚLTIPLAS EXPERIÊNCIAS → "
        "EVIDÊNCIA ACUMULADA: OK"
    )

    print(
        "TRANSFORMAÇÃO CORRETA → "
        "PRIORIDADE: OK"
    )

    print()
    print("=== PROBLEMA NOVO ===")

    add_code_node(
        graph,
        "source_new",
        NEW_SOURCE,
        {
            "role": "new_problem",
        },
    )

    result_new = search_problem(
        graph,
        "source_new",
        NEW_TESTS,
    )

    print(
        "Sucesso:",
        result_new.get("success"),
    )

    print(
        "Caminho:",
        result_new.get("path"),
    )

    if not result_new.get("success"):
        raise RuntimeError(
            "O problema novo não foi resolvido."
        )

    print()
    print("=== RESULTADO ===")
    print(
        "MÚLTIPLAS EXPERIÊNCIAS: OK"
    )
    print(
        "EVIDÊNCIA ACUMULADA: OK"
    )
    print(
        "CONTEXT GUIDANCE → DECISÃO: OK"
    )
    print(
        "NOVO PROBLEMA → RESOLVIDO: OK"
    )


if __name__ == "__main__":
    main()
