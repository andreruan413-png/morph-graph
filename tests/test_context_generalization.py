from graph.core import Graph
from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.experience import ExperienceRecorder
from engine.context_guidance import ContextGuidance


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


def train_experience(graph):
    graph.add_node(
        "problem_train",
        "problem",
        {
            "description": "problema de treinamento",
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

    result = search_problem(
        graph,
        "source_train",
        TRAIN_TESTS,
    )

    if not result.get("success"):
        raise RuntimeError(
            "Treinamento falhou."
        )

    recorder = ExperienceRecorder(graph)

    experience_id = recorder.record_solution(
        "problem_train",
        result,
    )

    if not experience_id:
        raise RuntimeError(
            "Experiência não registrada."
        )

    return result, experience_id


def main():
    graph = Graph()

    print("=== TREINAMENTO ===")

    train_result, experience_id = train_experience(
        graph
    )

    print(
        "Sucesso:",
        train_result.get("success"),
    )

    print(
        "Caminho aprendido:",
        train_result.get("path"),
    )

    print(
        "Experiência:",
        experience_id,
    )

    if train_result.get("path") != [
        "binop_0_add_to_sub"
    ]:
        raise RuntimeError(
            "O treinamento não aprendeu "
            "add_to_sub como esperado."
        )

    print()
    print("=== EXPERIÊNCIA APRENDIDA ===")

    guidance = ContextGuidance(graph)

    ranked_experiences = guidance.rank_experiences(
        NEW_SOURCE
    )

    for experience in ranked_experiences:
        print(
            experience["experience_id"],
            "| similaridade:",
            experience["similarity"],
            "| score:",
            experience["score"],
        )

    if not ranked_experiences:
        raise RuntimeError(
            "Nenhuma experiência recuperada."
        )

    best_experience = ranked_experiences[0]

    if best_experience["similarity"] < 0.9:
        raise RuntimeError(
            "A experiência estruturalmente "
            "semelhante não foi reconhecida."
        )

    print(
        "EXPERIÊNCIA ESTRUTURALMENTE "
        "SEMELHANTE: OK"
    )

    print()
    print("=== PROBLEMA NOVO ===")

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
            item["context_score"],
            "| região:",
            item["candidate"].region_index,
        )

    if not ranked:
        raise RuntimeError(
            "Nenhum candidato foi gerado."
        )

    best = ranked[0]["candidate"]

    print()
    print(
        "PRIMEIRO CANDIDATO:",
        best.name,
    )

    if best.name != "binop_0_add_to_sub":
        raise RuntimeError(
            "Generalização falhou: "
            "a transformação aprendida não "
            "foi priorizada no código novo."
        )

    print(
        "GENERALIZAÇÃO → PRIORIDADE: OK"
    )

    print()
    print("=== BUSCA DO PROBLEMA NOVO ===")

    # Criamos o código novo no mesmo grafo,
    # preservando as experiências aprendidas.
    if "source_new" not in graph.nodes:
        add_code_node(
            graph,
            "source_new",
            NEW_SOURCE,
            {
                "role": "new_problem",
            },
        )

    result = search_problem(
        graph,
        "source_new",
        NEW_TESTS,
    )

    print(
        "Sucesso:",
        result.get("success"),
    )

    print(
        "Caminho:",
        result.get("path"),
    )

    if not result.get("success"):
        raise RuntimeError(
            "O problema novo não foi resolvido."
        )

    print()
    print("=== RESULTADO ===")
    print(
        "GENERALIZAÇÃO ESTRUTURAL: OK"
    )
    print(
        "EXPERIÊNCIA → NOVO CÓDIGO: OK"
    )
    print(
        "CONTEXT GUIDANCE → DECISÃO: OK"
    )
    print(
        "PROBLEMA NOVO → RESOLVIDO: OK"
    )


if __name__ == "__main__":
    main()
