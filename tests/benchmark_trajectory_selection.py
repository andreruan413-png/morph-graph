import sys
import os
import copy
from statistics import mean

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.trajectory_guidance import TrajectoryGuidance


class NoGuidance:

    def priorities(self, path):
        return {}


# ============================================================
# EXPERIÊNCIAS DE TREINAMENTO
#
# Cada experiência representa uma família diferente.
# ============================================================

TRAINING = [
    {
        "id": "experience_add_mult",
        "path": [
            "binop_0_sub_to_add",
            "binop_1_add_to_mult"
        ]
    },
    {
        "id": "experience_swap",
        "path": [
            "binop_0_swap"
        ]
    },
    {
        "id": "experience_add_sub",
        "path": [
            "binop_0_add_to_sub"
        ]
    },
]


# ============================================================
# PROBLEMAS DE TESTE
#
# Cada problema pertence a uma família diferente.
# O sistema não recebe previamente qual família é.
# ============================================================

TEST_PROBLEMS = [

    # Família A:
    # precisa sub -> add
    # e depois add -> mult
    {
        "id": "family_a_01",
        "code": """
def resolver(x, y):
    return (x - y, x + y)
""",
        "tests": """
TEST: assert resolver(2, 3)[0] == 5
TEST: assert resolver(2, 3)[1] == 6
"""
    },

    {
        "id": "family_a_02",
        "code": """
def calcular(valor_a, valor_b):
    return (valor_a - valor_b, valor_a + valor_b)
""",
        "tests": """
TEST: assert calcular(4, 5)[0] == 9
TEST: assert calcular(4, 5)[1] == 20
"""
    },

    # Família B:
    # precisa trocar operandos.
    {
        "id": "family_b_01",
        "code": """
def inverter(a, b):
    return a - b
""",
        "tests": """
TEST: assert inverter(10, 3) == -7
"""
    },

    {
        "id": "family_b_02",
        "code": """
def calcular_ordem(esquerda, direita):
    return esquerda - direita
""",
        "tests": """
TEST: assert calcular_ordem(8, 2) == -6
"""
    },

    # Família C:
    # transformação add -> sub.
    {
        "id": "family_c_01",
        "code": """
def diferenca(a, b):
    return a + b
""",
        "tests": """
TEST: assert diferenca(10, 3) == 7
"""
    },

    {
        "id": "family_c_02",
        "code": """
def calcular_diferenca(valor1, valor2):
    return valor1 + valor2
""",
        "tests": """
TEST: assert calcular_diferenca(9, 4) == 5
"""
    },

]


def create_training_graph():

    graph = Graph()

    for item in TRAINING:

        experience_id = item["id"]

        graph.add_node(
            experience_id,
            "experience",
            {
                "problem_id": experience_id,
                "solution_node": f"{experience_id}_solution",
                "score": 1.0,
                "generations": [
                    {
                        "generation": index + 1,
                        "selected": {
                            "rule": rule
                        }
                    }
                    for index, rule
                    in enumerate(item["path"])
                ]
            }
        )

        graph.add_node(
            f"{experience_id}_solution",
            "code",
            {
                "code": "def solution(a, b):\n    return a",
                "language": "python"
            }
        )

    return graph


def solve(
    problem,
    training_graph=None,
    learned=False
):

    graph = Graph()

    if training_graph:

        graph.nodes = copy.deepcopy(
            training_graph.nodes
        )

        graph.edges = copy.deepcopy(
            training_graph.edges
        )

        graph.history = copy.deepcopy(
            training_graph.history
        )

    source_id = f"{problem['id']}_source"

    graph.add_node(
        source_id,
        "code",
        {
            "code": problem["code"],
            "language": "python"
        }
    )

    mutator = AutomaticASTMutator()

    evaluations = 0

    def evaluator(code):

        nonlocal evaluations

        evaluations += 1

        result = evaluate_problem(
            code,
            problem["tests"]
        )

        return {
            "success": result.success,
            "score": result.score,
            "reason": result.reason,
            "passed": result.passed,
            "total": result.total
        }

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3
    )

    if not learned:
        search.trajectory_guidance = NoGuidance()

    result = search.search(source_id)

    result["evaluations"] = evaluations

    return result


def main():

    print("=" * 72)
    print("     MORPH-GRAPH — SELEÇÃO DE TRAJETÓRIA")
    print("=" * 72)

    training_graph = create_training_graph()

    guidance = TrajectoryGuidance(
        training_graph
    )

    print()
    print("MEMÓRIA DE TREINAMENTO")
    print("-" * 72)

    memory = guidance.memory

    for trajectory in memory.successful_trajectories():

        print(
            trajectory["experience_id"],
            ":",
            " -> ".join(
                trajectory["path"]
            )
        )

    baseline_results = []
    learned_results = []

    print()
    print("TESTE EM FAMÍLIAS NOVAS")
    print("-" * 72)

    for index, problem in enumerate(
        TEST_PROBLEMS,
        start=1
    ):

        baseline = solve(
            problem,
            learned=False
        )

        learned = solve(
            problem,
            training_graph=training_graph,
            learned=True
        )

        baseline_results.append(
            baseline
        )

        learned_results.append(
            learned
        )

        print()
        print(
            f"Problema {index:02d} "
            f"[{problem['id']}]"
        )

        print(
            "  baseline :",
            f"explorados={baseline['explored']}",
            f"avaliacoes={baseline['evaluations']}",
            f"sucesso={baseline['success']}",
            f"caminho={baseline['path']}"
        )

        print(
            "  aprendido:",
            f"explorados={learned['explored']}",
            f"avaliacoes={learned['evaluations']}",
            f"sucesso={learned['success']}",
            f"caminho={learned['path']}"
        )

    total = len(TEST_PROBLEMS)

    baseline_success = sum(
        item["success"]
        for item in baseline_results
    )

    learned_success = sum(
        item["success"]
        for item in learned_results
    )

    baseline_explored = sum(
        item["explored"]
        for item in baseline_results
    )

    learned_explored = sum(
        item["explored"]
        for item in learned_results
    )

    baseline_evaluations = sum(
        item["evaluations"]
        for item in baseline_results
    )

    learned_evaluations = sum(
        item["evaluations"]
        for item in learned_results
    )

    baseline_depth = mean(
        item["best"]["depth"]
        for item in baseline_results
    )

    learned_depth = mean(
        item["best"]["depth"]
        for item in learned_results
    )

    if baseline_explored:

        exploration_reduction = (
            (
                baseline_explored
                - learned_explored
            )
            / baseline_explored
        ) * 100

    else:

        exploration_reduction = 0

    if baseline_evaluations:

        evaluation_reduction = (
            (
                baseline_evaluations
                - learned_evaluations
            )
            / baseline_evaluations
        ) * 100

    else:

        evaluation_reduction = 0

    print()
    print("=" * 72)
    print("RESULTADO FINAL")
    print("=" * 72)

    print(
        f"Problemas:                    {total}"
    )

    print(
        f"Baseline resolvidos:          "
        f"{baseline_success}/{total}"
    )

    print(
        f"Aprendido resolvidos:         "
        f"{learned_success}/{total}"
    )

    print()

    print(
        f"Baseline nós explorados:      "
        f"{baseline_explored}"
    )

    print(
        f"Aprendido nós explorados:     "
        f"{learned_explored}"
    )

    print(
        f"Redução da exploração:        "
        f"{exploration_reduction:.2f}%"
    )

    print()

    print(
        f"Baseline avaliações:          "
        f"{baseline_evaluations}"
    )

    print(
        f"Aprendido avaliações:         "
        f"{learned_evaluations}"
    )

    print(
        f"Redução de avaliações:        "
        f"{evaluation_reduction:.2f}%"
    )

    print()

    print(
        f"Profundidade média baseline:  "
        f"{baseline_depth:.2f}"
    )

    print(
        f"Profundidade média aprendido: "
        f"{learned_depth:.2f}"
    )

    print()
    print("=" * 72)

    if (
        learned_success == total
        and learned_explored <= baseline_explored
    ):

        print(
            "SELEÇÃO DE TRAJETÓRIA: OK"
        )

    else:

        print(
            "SELEÇÃO DE TRAJETÓRIA: "
            "PRECISA DE EVOLUÇÃO"
        )

    print("=" * 72)


if __name__ == "__main__":
    main()
