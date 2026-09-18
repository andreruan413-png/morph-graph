from graph.core import Graph
from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.experience import ExperienceRecorder


TRAIN_SOURCE = """def resolver(a, b):
    return a + b
"""

TRAIN_TESTS = """TEST: resolver(10, 3) == 7
TEST: resolver(20, 5) == 15
"""


NEW_SOURCE = """def resolver(x, y):
    return x + y
"""

NEW_TESTS = """TEST: resolver(100, 37) == 63
TEST: resolver(50, 12) == 38
"""


def run_search(
    graph,
    source_id,
    tests,
    use_context_guidance,
):
    evaluations = []

    mutator = AutomaticASTMutator()

    def evaluator(code):
        result = evaluate_problem(
            code,
            tests,
        ).as_dict()

        evaluations.append({
            "code": code,
            "score": result.get("score", 0.0),
            "success": result.get("success", False),
        })

        return result

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        use_context_guidance=use_context_guidance,
    )

    result = search.search(source_id)

    return result, evaluations


def train(graph):
    graph.add_node(
        "problem_train",
        "problem",
        {
            "description": "treinamento",
            "language": "python",
        },
    )

    add_code_node(
        graph,
        "source_train",
        TRAIN_SOURCE,
        {
            "role": "source",
        },
    )

    graph.connect(
        "problem_train",
        "source_train",
        "has_candidate",
    )

    result, evaluations = run_search(
        graph,
        "source_train",
        TRAIN_TESTS,
        False,
    )

    if not result.get("success"):
        raise RuntimeError(
            "Treinamento não encontrou solução."
        )

    recorder = ExperienceRecorder(graph)

    experience_id = recorder.record_solution(
        "problem_train",
        result,
    )

    if not experience_id:
        raise RuntimeError(
            "Experiência não foi registrada."
        )

    return result, experience_id, evaluations


def main():
    print("=== TREINAMENTO ===")

    graph_memory = Graph()

    train_result, experience_id, train_evaluations = train(
        graph_memory
    )

    print(
        "Caminho aprendido:",
        train_result.get("path"),
    )

    print(
        "Experiência:",
        experience_id,
    )

    print(
        "Avaliações no treinamento:",
        len(train_evaluations),
    )

    print()
    print("=== BASELINE — SEM MEMÓRIA ===")

    graph_baseline = Graph()

    add_code_node(
        graph_baseline,
        "source_new",
        NEW_SOURCE,
        {
            "role": "new_problem",
        },
    )

    baseline_result, baseline_evaluations = run_search(
        graph_baseline,
        "source_new",
        NEW_TESTS,
        False,
    )

    print(
        "Sucesso:",
        baseline_result.get("success"),
    )

    print(
        "Caminho:",
        baseline_result.get("path"),
    )

    print(
        "Avaliações:",
        len(baseline_evaluations),
    )

    print()
    print("=== COM MEMÓRIA ===")

    graph_context = graph_memory

    add_code_node(
        graph_context,
        "source_new",
        NEW_SOURCE,
        {
            "role": "new_problem",
        },
    )

    context_result, context_evaluations = run_search(
        graph_context,
        "source_new",
        NEW_TESTS,
        True,
    )

    print(
        "Sucesso:",
        context_result.get("success"),
    )

    print(
        "Caminho:",
        context_result.get("path"),
    )

    print(
        "Avaliações:",
        len(context_evaluations),
    )

    if not baseline_result.get("success"):
        raise RuntimeError(
            "Baseline não resolveu o problema."
        )

    if not context_result.get("success"):
        raise RuntimeError(
            "Busca com contexto não resolveu o problema."
        )

    baseline_count = len(baseline_evaluations)
    context_count = len(context_evaluations)

    if baseline_count == 0:
        raise RuntimeError(
            "Baseline não realizou avaliações."
        )

    reduction = (
        (baseline_count - context_count)
        / baseline_count
        * 100.0
    )

    print()
    print("=== COMPARAÇÃO ===")

    print(
        "Sem memória:",
        baseline_count,
        "avaliações",
    )

    print(
        "Com memória:",
        context_count,
        "avaliações",
    )

    print(
        "Redução:",
        round(reduction, 2),
        "%",
    )

    print()
    print("=== RESULTADO ===")

    if context_count < baseline_count:
        print(
            "VANTAGEM COMPUTACIONAL: OK"
        )
    elif context_count == baseline_count:
        print(
            "VANTAGEM COMPUTACIONAL: "
            "NÃO DEMONSTRADA"
        )
    else:
        print(
            "VANTAGEM COMPUTACIONAL: "
            "NEGATIVA"
        )

    print(
        "SEM MEMÓRIA → SOLUÇÃO: OK"
    )

    print(
        "COM MEMÓRIA → SOLUÇÃO: OK"
    )

    print(
        "MEMÓRIA → REDUÇÃO DE BUSCA: "
        f"{round(reduction, 2)}%"
    )


if __name__ == "__main__":
    main()
