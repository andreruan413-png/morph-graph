from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine
from engine.strategy import trajectory_statistics, rank_candidates
from engine.auto_mutation import AutomaticASTMutator


print("========================================")
print(" MORPH-GRAPH - TESTE DE MEMÓRIA")
print("========================================")


graph = Graph()


# ==================================================
# EXPERIÊNCIA 1
# ==================================================

program_a = """
def calcular(a, b):
    return a - b
"""

tests_a = """
TEST: assert candidate.calcular(10, 3) == 13
TEST: assert candidate.calcular(20, 5) == 25
"""


add_code_node(
    graph,
    "program_a",
    program_a,
    {
        "description": "experiência anterior"
    }
)


print("\n=== EXPERIÊNCIA 1 ===")

engine_a = EvolutionEngine(
    graph,
    tests=tests_a
)


result_a = engine_a.evolve(
    "program_a",
    generations=3
)


print(
    "\nResultado A:",
    result_a["final_node"]
)


# ==================================================
# MEMÓRIA
# ==================================================

print("\n=== MEMÓRIA DE TRAJETÓRIA ===")

trajectories = trajectory_statistics(
    graph
)


for index, trajectory in enumerate(
    trajectories,
    start=1
):

    print(
        f"{index}. "
        f"{trajectory['source_node']} "
        f"--[{trajectory['mutation']}]--> "
        f"{trajectory['target_node']} "
        f"| score={trajectory['score']}"
    )


print(
    "\nTotal de trajetórias:",
    len(trajectories)
)


# ==================================================
# EXPERIÊNCIA 2
# ==================================================

program_b = """
def resolver(x, y):
    return x - y
"""


tests_b = """
TEST: assert candidate.resolver(8, 2) == 10
TEST: assert candidate.resolver(15, 5) == 20
"""


add_code_node(
    graph,
    "program_b",
    program_b,
    {
        "description": "novo programa"
    }
)


print("\n=== NOVO PROGRAMA ===")

mutator = AutomaticASTMutator()

candidates = mutator.generate(
    program_b
)


ranked = rank_candidates(
    graph,
    "program_b",
    candidates
)


print("\n=== RANKING APRENDIDO ===")

for position, item in enumerate(
    ranked,
    start=1
):

    print(
        f"{position}. "
        f"{item['candidate'].name} "
        f"| hist_rate={item['success_rate']:.2f} "
        f"| avg_score={item['average_score']:.2f} "
        f"| trajectory={item['trajectory_score']:.2f} "
        f"| trajectory_count={item['trajectory_count']}"
    )


print("\n========================================")
print(" FIM DO TESTE")
print("========================================")
