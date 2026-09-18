from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine

graph = Graph()

problem = Problem(
    "problem_new_hard_bug",
    """
    Corrija a função calculate_score_v2.
    Ela recebe base, success_pts, error_pts e multiplier.
    Deve retornar a pontuação correta considerando ganhos e perdas.
    """,
    """
    TEST: assert calculate_score_v2(100, 10, 2, 5) == 140
    TEST: assert calculate_score_v2(200, 20, 5, 3) == 245
    TEST: assert calculate_score_v2(50, 5, 1, 10) == 90
    """
)

problem.add_to_graph(graph)

buggy_code = '''
def calculate_score_v2(base, success_pts, error_pts, multiplier):
    earned = success_pts * multiplier
    lost = error_pts * multiplier
    total = base + earned + lost
    return total
'''

add_code_node(
    graph,
    "candidate_new_hard",
    buggy_code,
)

graph.connect(
    "problem_new_hard_bug",
    "candidate_new_hard",
    "has_candidate",
)

engine = ProblemEngine(
    graph,
    "problem_new_hard_bug",
)

result = engine.solve(
    generations=8,
    beam_width=5,
)

print()
print("=" * 70)
print("MORPH-GRAPH — NOVO BENCHMARK DE HARD BUG")
print("=" * 70)
print()
print("Sucesso:", result.get("success"))
print("Score:", result.get("score"))
print("Caminho:", result.get("path"))
print("Candidatos avaliados:", len(result.get("evaluated_candidates", [])))
print("=" * 70)
