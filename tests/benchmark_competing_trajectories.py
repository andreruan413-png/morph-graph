from engine.problem_evaluator import evaluate_problem
from graph.core import Graph
from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.path_search import PathSearch
from engine.transition_memory import TransitionMemory
from engine.context_memory import ContextMemory


SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""


TRAINING = [
    {
        "name": "A",
        "tests": """TEST: resolver(10, 3) == (7, 13)
TEST: resolver(20, 5) == (15, 25)"""
    },
    {
        "name": "B",
        "tests": """TEST: resolver(10, 3) == (13, 30)
TEST: resolver(4, 5) == (9, 20)"""
    },
    {
        "name": "C",
        "tests": """TEST: resolver(10, 3) == (-7, 13)
TEST: resolver(20, 5) == (-15, 25)"""
    },
    {
        "name": "D",
        "tests": """TEST: resolver(10, 3) == (30, 13)
TEST: resolver(20, 5) == (100, 25)"""
    }
]


NEW_PROBLEMS = [
    {
        "name": "A1",
        "group": "A",
        "tests": """TEST: resolver(8, 2) == (6, 10)
TEST: resolver(15, 4) == (11, 19)"""
    },
    {
        "name": "A2",
        "group": "A",
        "tests": """TEST: resolver(12, 5) == (7, 17)
TEST: resolver(30, 10) == (20, 40)"""
    },
    {
        "name": "A3",
        "group": "A",
        "tests": """TEST: resolver(9, 1) == (8, 10)
TEST: resolver(25, 7) == (18, 32)"""
    },
    {
        "name": "B1",
        "group": "B",
        "tests": """TEST: resolver(8, 2) == (10, 16)
TEST: resolver(6, 4) == (10, 24)"""
    },
    {
        "name": "B2",
        "group": "B",
        "tests": """TEST: resolver(12, 5) == (17, 60)
TEST: resolver(7, 3) == (10, 21)"""
    },
    {
        "name": "B3",
        "group": "B",
        "tests": """TEST: resolver(9, 1) == (10, 9)
TEST: resolver(5, 4) == (9, 20)"""
    },
    {
        "name": "C1",
        "group": "C",
        "tests": """TEST: resolver(8, 2) == (-6, 10)
TEST: resolver(15, 4) == (-11, 19)"""
    },
    {
        "name": "C2",
        "group": "C",
        "tests": """TEST: resolver(12, 5) == (-7, 17)
TEST: resolver(30, 10) == (-20, 40)"""
    },
    {
        "name": "C3",
        "group": "C",
        "tests": """TEST: resolver(9, 1) == (-8, 10)
TEST: resolver(25, 7) == (-18, 32)"""
    },
    {
        "name": "D1",
        "group": "D",
        "tests": """TEST: resolver(8, 2) == (16, 10)
TEST: resolver(5, 3) == (15, 8)"""
    },
    {
        "name": "D2",
        "group": "D",
        "tests": """TEST: resolver(12, 5) == (60, 17)
TEST: resolver(7, 3) == (21, 10)"""
    },
    {
        "name": "D3",
        "group": "D",
        "tests": """TEST: resolver(9, 1) == (9, 10)
TEST: resolver(5, 4) == (20, 9)"""
    }
]


def add_source(graph):
    add_code_node(
        graph,
        "source",
        SOURCE,
        {
            "role": "source",
            "generated_by": "seed"
        }
    )


def discover(graph, tests, context_memory=None):
    memory = TransitionMemory(graph)

    evaluator = lambda code: evaluate_problem(
        code,
        tests
    ).as_dict()

    search = PathSearch(
        graph,
        AutomaticASTMutator(),
        evaluator,
        max_depth=4,
        beam_width=4,
        transition_memory=memory,
        context_memory=context_memory,
        context_tests=tests,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False
    )

    return search.search("source")


def train():
    graph = Graph()
    add_source(graph)

    context_memory = ContextMemory(graph)
    learned = {}

    print()
    print("TREINAMENTO DAS TRAJETÓRIAS")
    print()

    for item in TRAINING:
        result = discover(
            graph,
            item["tests"],
            context_memory=None
        )

        if not result.get("success"):
            print("Falha no treinamento:", item["name"])
            return None

        path = result.get("path", [])

        learned[item["name"]] = {
            "path": path,
            "tests": item["tests"]
        }

        context_memory.remember(
            item["tests"],
            path,
            score=1.0
        )

        print(
            "TRAJETÓRIA",
            item["name"],
            ":",
            path
        )

    return graph, context_memory, learned


def run_problem(graph, tests, context_memory=None):
    result = discover(
        graph,
        tests,
        context_memory=context_memory
    )

    return result


def main():
    trained = train()

    if trained is None:
        return

    graph, context_memory, learned = trained

    print()
    print("TRAJETÓRIAS APRENDIDAS")
    print()

    for name, data in learned.items():
        print(
            name,
            "=>",
            data["path"]
        )

    print()
    print("NOVOS PROBLEMAS")
    print()

    total_without = 0
    total_with = 0

    success_without = 0
    success_with = 0

    contextual_success = 0

    for problem in NEW_PROBLEMS:
        print()
        print("PROBLEMA", problem["name"])
        print("GRUPO:", problem["group"])

        result_without = run_problem(
            graph,
            problem["tests"],
            context_memory=None
        )

        result_with = run_problem(
            graph,
            problem["tests"],
            context_memory=context_memory
        )

        eval_without = result_without.get(
            "evaluated_candidates",
            result_without.get("evaluations", result_without.get("tested", 0))
        )

        eval_with = result_with.get(
            "evaluated_candidates",
            result_with.get("evaluations", result_with.get("tested", 0))
        )

        if not isinstance(eval_without, int):
            eval_without = int(eval_without or 0)

        if not isinstance(eval_with, int):
            eval_with = int(eval_with or 0)

        total_without += eval_without
        total_with += eval_with

        if result_without.get("success"):
            success_without += 1

        if result_with.get("success"):
            success_with += 1

        expected_path = learned[problem["group"]]["path"]
        actual_path = result_with.get("path", [])

        if result_with.get("success"):
            if actual_path == expected_path:
                contextual_success += 1

        print(
            "SEM MEMÓRIA:",
            result_without.get("success"),
            "caminho:",
            result_without.get("path", []),
            "avaliações:",
            eval_without
        )

        print(
            "COM MEMÓRIA:",
            result_with.get("success"),
            "caminho:",
            actual_path,
            "avaliações:",
            eval_with
        )

    print()
    print("RESULTADO FINAL")
    print()

    print(
        "Problemas testados:",
        len(NEW_PROBLEMS)
    )

    print(
        "Sucessos sem memória:",
        str(success_without) + "/" + str(len(NEW_PROBLEMS))
    )

    print(
        "Sucessos com memória:",
        str(success_with) + "/" + str(len(NEW_PROBLEMS))
    )

    print(
        "Trajetórias contextuais corretas:",
        str(contextual_success) + "/" + str(len(NEW_PROBLEMS))
    )

    print(
        "Avaliações sem memória:",
        total_without
    )

    print(
        "Avaliações com memória:",
        total_with
    )

    if total_without > 0:
        reduction = (
            (total_without - total_with)
            / total_without
            * 100
        )
    else:
        reduction = 0.0

    print(
        "Redução da busca:",
        f"{reduction:.2f}%"
    )

    print()
    print("VALIDAÇÃO")

    if success_with == len(NEW_PROBLEMS):
        print("TODOS OS PROBLEMAS: OK")
    else:
        print("TODOS OS PROBLEMAS: FALHA")

    if contextual_success == len(NEW_PROBLEMS):
        print("MEMÓRIA CONTEXTUAL: OK")
    else:
        print("MEMÓRIA CONTEXTUAL: FALHA")

    if total_with <= total_without:
        print("VANTAGEM COMPUTACIONAL: OK")
    else:
        print("VANTAGEM COMPUTACIONAL: FALHA")


if __name__ == "__main__":
    main()
