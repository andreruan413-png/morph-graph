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
from engine.trajectory_memory import TrajectoryMemory


# ============================================================
# MORPH-GRAPH
# BENCHMARK DE GENERALIZAÇÃO V2
#
# Objetivo:
#   verificar se experiências anteriores ajudam em problemas
#   estruturalmente relacionados, mas não idênticos.
#
# Métricas:
#   - resolução
#   - nós explorados
#   - profundidade
#   - comprimento do caminho
#   - avaliações
#   - reutilização da trajetória
# ============================================================


class NoGuidance:

    def priorities(self, path):
        return {}


def make_experience_graph(
    experience_id,
    problem_id,
    path
):
    graph = Graph()

    graph.add_node(
        f"{problem_id}_source",
        "code",
        {
            "code": "def treinamento(a, b):\n    return (a - b, a + b)",
            "language": "python"
        }
    )

    graph.add_node(
        f"{problem_id}_solution",
        "code",
        {
            "code": "def treinamento(a, b):\n    return (a + b, a * b)",
            "language": "python"
        }
    )

    generations = []

    for index, rule in enumerate(path):

        generations.append(
            {
                "generation": index + 1,
                "source": (
                    f"{problem_id}_source"
                    if index == 0
                    else f"intermediate_{index}"
                ),
                "selected": {
                    "rule": rule,
                    "node_id": (
                        f"{problem_id}_solution"
                        if index == len(path) - 1
                        else f"intermediate_{index + 1}"
                    )
                }
            }
        )

    graph.add_node(
        experience_id,
        "experience",
        {
            "problem_id": problem_id,
            "solution_node": f"{problem_id}_solution",
            "score": 1.0,
            "generations": generations
        }
    )

    return graph


def merge_graphs(graphs):

    result = Graph()

    for graph in graphs:

        for node_id, node in graph.nodes.items():

            if node_id not in result.nodes:
                result.nodes[node_id] = copy.deepcopy(node)

        result.edges.extend(
            copy.deepcopy(graph.edges)
        )

        result.history.extend(
            copy.deepcopy(graph.history)
        )

    return result


TRAINING = [

    (
        "experience_train_01",
        "train_01",
        [
            "binop_0_sub_to_add",
            "binop_1_add_to_mult"
        ]
    ),

    (
        "experience_train_02",
        "train_02",
        [
            "binop_0_sub_to_add",
            "binop_1_add_to_mult"
        ]
    ),

    (
        "experience_train_03",
        "train_03",
        [
            "binop_0_sub_to_add",
            "binop_1_add_to_mult"
        ]
    ),
]


# ============================================================
# PROBLEMAS DE TESTE
#
# Eles NÃO entram na memória durante o treinamento.
# ============================================================

TESTS = [

    {
        "id": "general_01",
        "code": """
def resolver_esquerda(x, y):
    return (x - y, x + y)
""",
        "tests": """
TEST: assert resolver_esquerda(2, 3)[0] == 5
TEST: assert resolver_esquerda(2, 3)[1] == 6
"""
    },

    {
        "id": "general_02",
        "code": """
def combinar_valores(primeiro, segundo):
    return (primeiro - segundo, primeiro + segundo)
""",
        "tests": """
TEST: assert combinar_valores(5, 4)[0] == 9
TEST: assert combinar_valores(5, 4)[1] == 20
"""
    },

    {
        "id": "general_03",
        "code": """
def gerar_resultado(a1, b1):
    return (a1 - b1, a1 + b1)
""",
        "tests": """
TEST: assert gerar_resultado(7, 2)[0] == 9
TEST: assert gerar_resultado(7, 2)[1] == 14
"""
    },

    {
        "id": "general_04",
        "code": """
def transformar_dados(left, right):
    return (left - right, left + right)
""",
        "tests": """
TEST: assert transformar_dados(8, 3)[0] == 11
TEST: assert transformar_dados(8, 3)[1] == 24
"""
    },

    {
        "id": "general_05",
        "code": """
def produzir_saida(valor_x, valor_y):
    return (valor_x - valor_y, valor_x + valor_y)
""",
        "tests": """
TEST: assert produzir_saida(9, 5)[0] == 14
TEST: assert produzir_saida(9, 5)[1] == 45
"""
    },

    {
        "id": "general_06",
        "code": """
def calcular_par(numero_a, numero_b):
    return (numero_a - numero_b, numero_a + numero_b)
""",
        "tests": """
TEST: assert calcular_par(10, 4)[0] == 14
TEST: assert calcular_par(10, 4)[1] == 40
"""
    },

    {
        "id": "general_07",
        "code": """
def operar_elementos(first_value, second_value):
    return (first_value - second_value, first_value + second_value)
""",
        "tests": """
TEST: assert operar_elementos(11, 6)[0] == 17
TEST: assert operar_elementos(11, 6)[1] == 66
"""
    },

    {
        "id": "general_08",
        "code": """
def processar_pares(p, q):
    return (p - q, p + q)
""",
        "tests": """
TEST: assert processar_pares(12, 7)[0] == 19
TEST: assert processar_pares(12, 7)[1] == 84
"""
    },

]


def solve(
    problem,
    training_graph=None,
    learned=False
):

    graph = Graph()

    if training_graph is not None:

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

    evaluation_count = 0

    def evaluator(code):

        nonlocal evaluation_count

        evaluation_count += 1

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

    result["evaluations"] = evaluation_count

    return result


def trajectory_report(graph):

    memory = TrajectoryMemory(graph)

    trajectories = memory.successful_trajectories()

    print()
    print("TRAJETÓRIAS APRENDIDAS")
    print("-" * 70)

    for trajectory in trajectories:

        print(
            trajectory["experience_id"],
            ":",
            " -> ".join(
                trajectory["path"]
            )
        )

    return trajectories


def main():

    print("=" * 70)
    print("       MORPH-GRAPH — GENERALIZAÇÃO V2")
    print("=" * 70)

    print()
    print("FASE 1 — CONSTRUINDO MEMÓRIA DE TREINAMENTO")
    print("-" * 70)

    training_graphs = []

    for (
        experience_id,
        problem_id,
        path
    ) in TRAINING:

        graph = make_experience_graph(
            experience_id,
            problem_id,
            path
        )

        training_graphs.append(graph)

        print(
            f"{experience_id}: "
            + " -> ".join(path)
        )

    training_memory = merge_graphs(
        training_graphs
    )

    trajectories = trajectory_report(
        training_memory
    )

    print()
    print(
        "Total de trajetórias:",
        len(trajectories)
    )

    print()
    print("FASE 2 — PROBLEMAS NUNCA VISTOS")
    print("-" * 70)

    baseline_results = []
    learned_results = []

    for index, problem in enumerate(
        TESTS,
        start=1
    ):

        baseline = solve(
            problem,
            learned=False
        )

        learned = solve(
            problem,
            training_graph=training_memory,
            learned=True
        )

        baseline_results.append(baseline)
        learned_results.append(learned)

        print()
        print(
            f"Problema {index:02d}"
        )

        print(
            f"  baseline : "
            f"explorados={baseline['explored']} "
            f"avaliacoes={baseline['evaluations']} "
            f"depth={baseline['best']['depth']} "
            f"sucesso={baseline['success']}"
        )

        print(
            f"  aprendido: "
            f"explorados={learned['explored']} "
            f"avaliacoes={learned['evaluations']} "
            f"depth={learned['best']['depth']} "
            f"sucesso={learned['success']}"
        )

        print(
            "  caminho baseline :",
            " -> ".join(
                baseline["path"]
            )
        )

        print(
            "  caminho aprendido:",
            " -> ".join(
                learned["path"]
            )
        )

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    baseline_explored = sum(
        item["explored"]
        for item in baseline_results
    )

    learned_explored = sum(
        item["explored"]
        for item in learned_results
    )

    baseline_eval = sum(
        item["evaluations"]
        for item in baseline_results
    )

    learned_eval = sum(
        item["evaluations"]
        for item in learned_results
    )

    baseline_success = sum(
        item["success"]
        for item in baseline_results
    )

    learned_success = sum(
        item["success"]
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

    baseline_path = mean(
        len(item["path"])
        for item in baseline_results
    )

    learned_path = mean(
        len(item["path"])
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

    if baseline_eval:

        evaluation_reduction = (
            (
                baseline_eval
                - learned_eval
            )
            / baseline_eval
        ) * 100

    else:

        evaluation_reduction = 0

    total = len(TESTS)

    print()
    print("=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)

    print(
        f"Problemas novos:              {total}"
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
        f"{baseline_eval}"
    )

    print(
        f"Aprendido avaliações:         "
        f"{learned_eval}"
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

    print(
        f"Caminho médio baseline:       "
        f"{baseline_path:.2f}"
    )

    print(
        f"Caminho médio aprendido:      "
        f"{learned_path:.2f}"
    )

    print()
    print("=" * 70)

    if (
        learned_success == total
        and learned_explored < baseline_explored
    ):

        print(
            "GENERALIZAÇÃO V2: "
            "APRENDIZAGEM TRANSFERIDA"
        )

    elif learned_success == total:

        print(
            "GENERALIZAÇÃO V2: "
            "RESOLVEU, MAS SEM REDUÇÃO"
        )

    else:

        print(
            "GENERALIZAÇÃO V2: "
            "AINDA INCOMPLETA"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()
