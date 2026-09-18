from graph.core import Graph

from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.transition_memory import TransitionMemory
from engine.context_memory import ContextMemory


SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""


# ============================================================
# PROBLEMAS DE TREINAMENTO
# ============================================================

TRAINING = [
    {
        "name": "A",
        "tests": """
TEST: resolver(10, 3) == (7, 13)
TEST: resolver(20, 5) == (15, 25)
"""
    },
    {
        "name": "B",
        "tests": """
TEST: resolver(10, 3) == (13, 30)
TEST: resolver(4, 5) == (9, 20)
"""
    }
]


# ============================================================
# PROBLEMAS NOVOS
# ============================================================

PROBLEMS = [
    {
        "name": "A1",
        "context": "A",
        "tests": """
TEST: resolver(8, 2) == (6, 10)
TEST: resolver(30, 4) == (26, 34)
"""
    },
    {
        "name": "A2",
        "context": "A",
        "tests": """
TEST: resolver(15, 6) == (9, 21)
TEST: resolver(40, 7) == (33, 47)
"""
    },
    {
        "name": "A3",
        "context": "A",
        "tests": """
TEST: resolver(12, 4) == (8, 16)
TEST: resolver(25, 10) == (15, 35)
"""
    },
    {
        "name": "A4",
        "context": "A",
        "tests": """
TEST: resolver(18, 5) == (13, 23)
TEST: resolver(50, 8) == (42, 58)
"""
    },
    {
        "name": "A5",
        "context": "A",
        "tests": """
TEST: resolver(21, 9) == (12, 30)
TEST: resolver(60, 11) == (49, 71)
"""
    },
    {
        "name": "B1",
        "context": "B",
        "tests": """
TEST: resolver(7, 2) == (9, 14)
TEST: resolver(6, 4) == (10, 24)
"""
    },
    {
        "name": "B2",
        "context": "B",
        "tests": """
TEST: resolver(9, 3) == (12, 27)
TEST: resolver(5, 6) == (11, 30)
"""
    },
    {
        "name": "B3",
        "context": "B",
        "tests": """
TEST: resolver(8, 5) == (13, 40)
TEST: resolver(4, 7) == (11, 28)
"""
    },
    {
        "name": "B4",
        "context": "B",
        "tests": """
TEST: resolver(11, 4) == (15, 44)
TEST: resolver(3, 8) == (11, 24)
"""
    },
    {
        "name": "B5",
        "context": "B",
        "tests": """
TEST: resolver(13, 2) == (15, 26)
TEST: resolver(6, 7) == (13, 42)
"""
    }
]


# ============================================================
# DESCOBRIR TRAJETÓRIA DE TREINAMENTO
# ============================================================

def discover(graph, tests):

    mutator = AutomaticASTMutator()

    def evaluator(code):
        return evaluate_problem(
            code,
            tests
        ).as_dict()

    transition_memory = TransitionMemory(graph)

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        transition_memory=transition_memory
    )

    return search.search("source")


# ============================================================
# EXECUTAR PROBLEMA
# ============================================================

def run_problem(tests, context_memory=None):

    graph = Graph()

    add_code_node(
        graph,
        "source",
        SOURCE,
        {
            "role": "source"
        }
    )

    mutator = AutomaticASTMutator()

    def evaluator(code):
        return evaluate_problem(
            code,
            tests
        ).as_dict()

    transition_memory = TransitionMemory(graph)

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        transition_memory=transition_memory,
        context_memory=context_memory,
        context_tests=tests
    )

    return search.search("source")


# ============================================================
# TREINAR MEMÓRIA
# ============================================================

def train_memory():

    graph = Graph()

    add_code_node(
        graph,
        "source",
        SOURCE,
        {
            "role": "source"
        }
    )

    context_memory = ContextMemory(graph)

    training_paths = {}

    for item in TRAINING:

        result = discover(
            graph,
            item["tests"]
        )

        if not result["success"]:
            raise RuntimeError(
                f"Falha no treinamento {item['name']}"
            )

        training_paths[
            item["name"]
        ] = result["path"]

        context_memory.remember(
            item["tests"],
            result["path"],
            score=1.0
        )

    return (
        context_memory,
        training_paths
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("MORPH-GRAPH")
    print("BENCHMARK DE ESCALA — MEMÓRIA CONTEXTUAL")
    print("=" * 70)

    # ========================================================
    # TREINAMENTO
    # ========================================================

    context_memory, training_paths = (
        train_memory()
    )

    print()
    print("=" * 70)
    print("TRAJETÓRIAS DE TREINAMENTO")
    print("=" * 70)

    for name, path in training_paths.items():

        print(
            name,
            ":",
            path
        )

    # ========================================================
    # RESULTADOS
    # ========================================================

    results = []

    total_without = 0
    total_with = 0

    successes_without = 0
    successes_with = 0

    # ========================================================
    # EXECUTAR TODOS OS PROBLEMAS
    # ========================================================

    for problem in PROBLEMS:

        print()
        print("-" * 70)
        print(
            "PROBLEMA:",
            problem["name"],
            "| CONTEXTO:",
            problem["context"]
        )
        print("-" * 70)

        # ----------------------------------------------------
        # SEM MEMÓRIA
        # ----------------------------------------------------

        without = run_problem(
            problem["tests"]
        )

        # ----------------------------------------------------
        # COM MEMÓRIA
        # ----------------------------------------------------

        with_memory = run_problem(
            problem["tests"],
            context_memory
        )

        evaluations_without = (
            without[
                "evaluated_candidates"
            ]
        )

        evaluations_with = (
            with_memory[
                "evaluated_candidates"
            ]
        )

        total_without += evaluations_without
        total_with += evaluations_with

        successes_without += int(
            without["success"]
        )

        successes_with += int(
            with_memory["success"]
        )

        results.append(
            {
                "name": problem["name"],
                "context": problem["context"],
                "without": without,
                "with": with_memory
            }
        )

        print(
            "SEM:",
            without["path"],
            "| avaliações:",
            evaluations_without,
            "| sucesso:",
            without["success"]
        )

        print(
            "COM:",
            with_memory["path"],
            "| avaliações:",
            evaluations_with,
            "| sucesso:",
            with_memory["success"]
        )

    # ========================================================
    # REDUÇÃO
    # ========================================================

    if total_without:

        reduction = (
            (
                total_without
                - total_with
            )
            /
            total_without
        ) * 100

    else:

        reduction = 0.0

    # ========================================================
    # MÉDIA
    # ========================================================

    count = len(PROBLEMS)

    average_without = (
        total_without / count
        if count
        else 0.0
    )

    average_with = (
        total_with / count
        if count
        else 0.0
    )

    # ========================================================
    # TRAJETÓRIAS CORRETAS
    # ========================================================

    correct_paths = 0

    for item in results:

        expected = training_paths[
            item["context"]
        ]

        actual = item["with"][
            "path"
        ]

        if actual == expected:

            correct_paths += 1

    # ========================================================
    # RESULTADO FINAL
    # ========================================================

    print()
    print("=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)

    print(
        "Problemas testados:",
        count
    )

    print(
        "Avaliações sem memória:",
        total_without
    )

    print(
        "Avaliações com memória:",
        total_with
    )

    print(
        "Média sem memória:",
        f"{average_without:.2f}"
    )

    print(
        "Média com memória:",
        f"{average_with:.2f}"
    )

    print(
        "Redução total:",
        f"{reduction:.2f}%"
    )

    print(
        "Sucessos sem memória:",
        f"{successes_without}/{count}"
    )

    print(
        "Sucessos com memória:",
        f"{successes_with}/{count}"
    )

    print(
        "Trajetórias contextuais corretas:",
        f"{correct_paths}/{count}"
    )

    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    success_rate_ok = (
        successes_with == count
    )

    contextual_selection_ok = (
        correct_paths == count
    )

    computational_advantage = (
        total_with < total_without
    )

    print()
    print("=" * 70)
    print("VALIDAÇÃO")
    print("=" * 70)

    print(
        "SUCESSO DOS PROBLEMAS:",
        "OK"
        if success_rate_ok
        else "FALHOU"
    )

    print(
        "SELEÇÃO CONTEXTUAL:",
        "OK"
        if contextual_selection_ok
        else "FALHOU"
    )

    print(
        "VANTAGEM COMPUTACIONAL:",
        "OK"
        if computational_advantage
        else "FALHOU"
    )

    if (
        success_rate_ok
        and contextual_selection_ok
        and computational_advantage
    ):

        print()
        print(
            "BENCHMARK DE ESCALA: OK"
        )

    else:

        print()
        print(
            "BENCHMARK DE ESCALA: "
            "AINDA INCOMPLETO"
        )


if __name__ == "__main__":
    main()
