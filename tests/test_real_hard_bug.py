from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine


graph = Graph()

problem = Problem(
    "problem_hard_real",
    """
    Corrija a função calculate_score.
    Ela recebe:
      base: pontuação inicial
      correct: número de respostas corretas
      wrong: número de respostas erradas
      streak: sequência de acertos
      bonus: bônus adicional

    A função deve retornar a pontuação final.
    """,
    """
TEST: assert calculate_score(100, 8, 2, 3, 10) == 199
TEST: assert calculate_score(250, 15, 4, 5, 20) == 434
TEST: assert calculate_score(80, 6, 1, 2, 5) == 153
TEST: assert calculate_score(500, 20, 7, 4, 30) == 734
TEST: assert calculate_score(175, 10, 3, 6, 15) == 306
""",
)

problem.add_to_graph(graph)

buggy_code = '''
def calculate_score(base, correct, wrong, streak, bonus):
    accuracy = correct * 10
    penalty = wrong * 3
    streak_bonus = streak * 2

    intermediate = (
        base
        + accuracy
        - penalty
        + streak_bonus
        + bonus
    )

    adjustment = (
        correct
        + streak
        - wrong
    )

    final_score = (
        intermediate
        + adjustment
    )

    return final_score
'''

add_code_node(
    graph,
    "candidate_hard",
    buggy_code,
)

graph.connect(
    "problem_hard_real",
    "candidate_hard",
    "has_candidate",
)

engine = ProblemEngine(
    graph,
    "problem_hard_real",
)

result = engine.solve(
    generations=8,
    beam_width=5,
)

print()
print("=" * 70)
print("MORPH-GRAPH — TESTE REAL DE BUG DIFÍCIL")
print("=" * 70)

print()
print("Sucesso:", result.get("success"))
print("Score:", result.get("score"))
print("Caminho:", result.get("path"))
print("Nó final:", result.get("node_id"))
print("Experiência:", result.get("experience_node"))

print()
print("CANDIDATOS AVALIADOS:", len(
    result.get("evaluated_candidates", [])
))

print()
print("DECISÕES NO GRAFO:")

decisions = [
    node
    for node in graph.nodes.values()
    if node.get("type") == "decision"
]

for decision in decisions:
    data = decision.get("data", {})
    print(
        decision["id"],
        "|",
        data.get("candidate"),
        "| mutation:",
        data.get("mutation_type"),
        "| region:",
        data.get("region_index"),
        "| score:",
        data.get("scores", {}).get("total"),
        "| useful:",
        data.get("useful"),
    )

print()
print("EXPERIÊNCIAS:")

experiences = [
    node
    for node in graph.nodes.values()
    if node.get("type") == "experience"
]

for experience in experiences:
    data = experience.get("data", {})
    print(
        experience["id"],
        "| solution:",
        data.get("solution_node"),
        "| score:",
        data.get("score"),
        "| trajectory:",
        data.get("trajectory"),
    )

print()
print("=" * 70)

if result.get("success"):
    print("BUG REAL RESOLVIDO PELO MORPH-GRAPH → OK")
else:
    print("MORPH-GRAPH NÃO RESOLVEU ESTE BUG")

print("=" * 70)
