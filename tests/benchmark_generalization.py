import sys
import os
import copy

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


# ============================================================
# MORPH-GRAPH — BENCHMARK DE GENERALIZAÇÃO
#
# Treino:
#   problemas vistos pelo sistema
#
# Teste:
#   problemas estruturalmente semelhantes,
#   mas com nomes/código diferentes.
#
# Comparamos:
#   1. busca sem memória
#   2. busca com memória de trajetórias
# ============================================================


TRAIN_PROBLEMS = [
    {
        "id": "train_01",
        "code": """
def calcular(a, b):
    return (a - b, a + b)
""",
        "tests": """
TEST: assert calcular(2, 3)[0] == 5
TEST: assert calcular(2, 3)[1] == 6
"""
    },
    {
        "id": "train_02",
        "code": """
def operar(x, y):
    return (x - y, x + y)
""",
        "tests": """
TEST: assert operar(5, 2)[0] == 7
TEST: assert operar(5, 2)[1] == 14
"""
    },
    {
        "id": "train_03",
        "code": """
def processar(p, q):
    return (p - q, p + q)
""",
        "tests": """
TEST: assert processar(4, 1)[0] == 5
TEST: assert processar(4, 1)[1] == 20
"""
    },
]


TEST_PROBLEMS = [
    {
        "id": "test_01",
        "code": """
def resolver(m, n):
    return (m - n, m + n)
""",
        "tests": """
TEST: assert resolver(3, 4)[0] == 7
TEST: assert resolver(3, 4)[1] == 12
"""
    },
    {
        "id": "test_02",
        "code": """
def transformar(valor_a, valor_b):
    return (valor_a - valor_b, valor_a + valor_b)
""",
        "tests": """
TEST: assert transformar(6, 2)[0] == 8
TEST: assert transformar(6, 2)[1] == 16
"""
    },
    {
        "id": "test_03",
        "code": """
def calcular_resultado(esquerda, direita):
    return (esquerda - direita, esquerda + direita)
""",
        "tests": """
TEST: assert calcular_resultado(7, 3)[0] == 10
TEST: assert calcular_resultado(7, 3)[1] == 21
"""
    },
    {
        "id": "test_04",
        "code": """
def combinar(first, second):
    return (first - second, first + second)
""",
        "tests": """
TEST: assert combinar(8, 5)[0] == 13
TEST: assert combinar(8, 5)[1] == 40
"""
    },
    {
        "id": "test_05",
        "code": """
def executar(a1, b1):
    return (a1 - b1, a1 + b1)
""",
        "tests": """
TEST: assert executar(9, 4)[0] == 13
TEST: assert executar(9, 4)[1] == 52
"""
    },
]


class NoGuidance:

    def priorities(self, path):
        return {}


def solve_problem(problem, learned=False, training_graph=None):

    graph = Graph()

    # Copia experiências de treinamento para o grafo de teste.
    if training_graph is not None:
        graph.nodes = copy.deepcopy(training_graph.nodes)
        graph.edges = copy.deepcopy(training_graph.edges)
        graph.history = copy.deepcopy(training_graph.history)

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

    def evaluator(code):
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

    return result


def create_training_experience(problem):

    graph = Graph()

    source_id = f"{problem['id']}_source"
    solution_id = f"{problem['id']}_solution"

    graph.add_node(
        source_id,
        "code",
        {
            "code": problem["code"],
            "language": "python"
        }
    )

    # A trajetória conhecida é:
    #
    # sub -> add
    # add -> mult
    #
    # exatamente o tipo de conhecimento que queremos
    # transferir para problemas estruturalmente semelhantes.

    graph.add_node(
        solution_id,
        "code",
        {
            "code": """
def solution(a, b):
    return (a + b, a * b)
""",
            "language": "python"
        }
    )

    graph.add_node(
        f"{problem['id']}_experience",
        "experience",
        {
            "problem_id": problem["id"],
            "solution_node": solution_id,
            "score": 1.0,
            "generations": [
                {
                    "source": source_id,
                    "selected": {
                        "rule": "binop_0_sub_to_add",
                        "node_id": "intermediate"
                    }
                },
                {
                    "source": "intermediate",
                    "selected": {
                        "rule": "binop_1_add_to_mult",
                        "node_id": solution_id
                    }
                }
            ]
        }
    )

    return graph


def merge_training_graphs(graphs):

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


def main():

    print("=" * 70)
    print("      MORPH-GRAPH — GENERALIZAÇÃO DE APRENDIZAGEM")
    print("=" * 70)

    print()
    print("FASE 1 — TREINAMENTO")
    print("-" * 70)

    training_graphs = []

    for problem in TRAIN_PROBLEMS:

        graph = create_training_experience(problem)

        training_graphs.append(graph)

        print(
            f"Experiência aprendida: {problem['id']} "
            f"-> sub_to_add -> add_to_mult"
        )

    training_memory = merge_training_graphs(
        training_graphs
    )

    print()
    print(
        "Experiências disponíveis:",
        len([
            node
            for node in training_memory.nodes.values()
            if node["type"] == "experience"
        ])
    )

    print()
    print("FASE 2 — TESTE EM PROBLEMAS NOVOS")
    print("-" * 70)

    baseline_total = 0
    learned_total = 0

    baseline_success = 0
    learned_success = 0

    baseline_depth = 0
    learned_depth = 0

    baseline_paths = []
    learned_paths = []

    for index, problem in enumerate(
        TEST_PROBLEMS,
        start=1
    ):

        baseline = solve_problem(
            problem,
            learned=False
        )

        learned = solve_problem(
            problem,
            learned=True,
            training_graph=training_memory
        )

        baseline_total += baseline["explored"]
        learned_total += learned["explored"]

        if baseline["success"]:
            baseline_success += 1

        if learned["success"]:
            learned_success += 1

        baseline_depth += baseline["best"]["depth"]
        learned_depth += learned["best"]["depth"]

        baseline_paths.append(
            baseline["path"]
        )

        learned_paths.append(
            learned["path"]
        )

        print(
            f"Problema novo {index:02d}: "
            f"baseline={baseline['explored']} | "
            f"aprendido={learned['explored']} | "
            f"depth={baseline['best']['depth']}/"
            f"{learned['best']['depth']}"
        )

        print(
            f"   baseline: {'OK' if baseline['success'] else 'FALHOU'} "
            f"{baseline['path']}"
        )

        print(
            f"   aprendido: {'OK' if learned['success'] else 'FALHOU'} "
            f"{learned['path']}"
        )

    total_problems = len(TEST_PROBLEMS)

    reduction = 0.0

    if baseline_total:
        reduction = (
            (baseline_total - learned_total)
            / baseline_total
        ) * 100

    print()
    print("=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)

    print(
        f"Problemas novos:              {total_problems}"
    )

    print(
        f"Baseline resolvidos:           "
        f"{baseline_success}/{total_problems}"
    )

    print(
        f"Aprendido resolvidos:          "
        f"{learned_success}/{total_problems}"
    )

    print(
        f"Baseline nós explorados:       "
        f"{baseline_total}"
    )

    print(
        f"Aprendido nós explorados:      "
        f"{learned_total}"
    )

    print(
        f"Redução da busca:              "
        f"{reduction:.2f}%"
    )

    print(
        f"Profundidade média baseline:   "
        f"{baseline_depth / total_problems:.2f}"
    )

    print(
        f"Profundidade média aprendido:  "
        f"{learned_depth / total_problems:.2f}"
    )

    print()
    print("CAMINHOS BASELINE:")

    for index, path in enumerate(
        baseline_paths,
        start=1
    ):
        print(
            f"{index:02d}: "
            + " -> ".join(path)
        )

    print()
    print("CAMINHOS APRENDIDOS:")

    for index, path in enumerate(
        learned_paths,
        start=1
    ):
        print(
            f"{index:02d}: "
            + " -> ".join(path)
        )

    print()
    print("=" * 70)

    if learned_success == total_problems:
        print("GENERALIZAÇÃO: OK")
    else:
        print(
            "GENERALIZAÇÃO: INCOMPLETA — "
            "precisamos ajustar a transferência."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()
