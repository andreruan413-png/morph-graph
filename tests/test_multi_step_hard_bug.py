from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine

graph = Graph()

problem = Problem(
    "problem_multi_step",
    """
    Corrija a função calculate_tiered_revenue.
    A função processa uma taxa base, volume, bonus_factor e penalty.
    Regra correta:
    1. step1 deve subtrair o ajuste de bonus (base_fee - (volume * bonus_factor))
    2. total deve somar a penalidade em vez de multiplicar (step1 + penalty)
    """,
    """
    TEST: assert calculate_tiered_revenue(100, 5, 2, 10) == 100
    TEST: assert calculate_tiered_revenue(200, 10, 3, 25) == 195
    TEST: assert calculate_tiered_revenue(50, 2, 4, 5) == 47
    """
)

problem.add_to_graph(graph)

buggy_code = '''
def calculate_tiered_revenue(base_fee, volume, bonus_factor, penalty):
    step1 = base_fee + (volume * bonus_factor)
    total = step1 * penalty
    return total
'''

add_code_node(
    graph,
    "candidate_multi_step_buggy",
    buggy_code,
)

graph.connect(
    "problem_multi_step",
    "candidate_multi_step_buggy",
    "has_candidate",
)

engine = ProblemEngine(
    graph,
    "problem_multi_step",
)

result = engine.solve(
    generations=6,
    beam_width=5,
)

print()
print("=" * 70)
print("MORPH-GRAPH — SEGUNDO BENCHMARK DE MÚLTIPLOS PASSOS")
print("=" * 70)
print()
print("Sucesso:", result.get("success"))
print("Score:", result.get("score"))
print("Caminho:", result.get("path"))
print("Candidatos avaliados:", len(result.get("evaluated_candidates", [])))
print("=" * 70)
