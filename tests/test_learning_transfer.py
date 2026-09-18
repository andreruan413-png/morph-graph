from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine


def build_problem_graph(problem_id, description, tests, candidate_id, code):
    graph = Graph()

    problem = Problem(problem_id, description, tests)
    problem.add_to_graph(graph)

    add_code_node(graph, candidate_id, code)
    graph.connect(problem_id, candidate_id, "has_candidate")

    return graph


print("=" * 70)
print("MORPH-GRAPH — EXPERIMENTO DE TRANSFERÊNCIA DE APRENDIZADO")
print("=" * 70)

source_tests = """
TEST: assert calculate_tiered_revenue(100, 5, 2, 10) == 100
TEST: assert calculate_tiered_revenue(200, 10, 3, 25) == 195
TEST: assert calculate_tiered_revenue(50, 2, 4, 5) == 47
"""

source_code = """
def calculate_tiered_revenue(base_fee, volume, bonus_factor, penalty):
    step1 = base_fee + (volume * bonus_factor)
    total = step1 * penalty
    return total
"""

shipping_description = """
Corrija a função calculate_shipping_tier.
A função processa base_cost, distance, weight_factor e handling_fee.

Regra correta:
1. subtotal deve subtrair o ajuste:
   base_cost - (distance * weight_factor)
2. total deve somar a taxa de manuseio:
   subtotal + handling_fee
"""

shipping_tests = """
TEST: assert calculate_shipping_tier(100, 5, 2, 10) == 100
TEST: assert calculate_shipping_tier(200, 10, 3, 25) == 195
TEST: assert calculate_shipping_tier(50, 2, 4, 5) == 47
"""

shipping_code = """
def calculate_shipping_tier(base_cost, distance, weight_factor, handling_fee):
    subtotal = base_cost + (distance * weight_factor)
    total = subtotal * handling_fee
    return total
"""

# ------------------------------------------------------------------
# FASE 0 — APRENDER A EXPERIÊNCIA DE ORIGEM
# ------------------------------------------------------------------

print("\n[FASE 0] Aprendendo experiência de origem...")

graph_source = build_problem_graph(
    "problem_multi_step",
    "Problema anterior de múltiplos passos",
    source_tests,
    "candidate_multi_step_buggy",
    source_code,
)

engine_source = ProblemEngine(
    graph_source,
    "problem_multi_step",
)

res_source = engine_source.solve(
    generations=6,
    beam_width=5,
)

experience_id = res_source.get("experience_node")

print("Experiência produzida:", experience_id)
print("Sucesso da origem:", res_source.get("success"))
print("Score da origem:", res_source.get("score"))

if not experience_id:
    raise RuntimeError("A execução de origem não produziu experience_node.")

if experience_id not in graph_source.nodes:
    raise RuntimeError(
        f"Experiência {experience_id} não encontrada em graph_source.nodes."
    )

experience_node = graph_source.nodes[experience_id]

if experience_node.get("type") != "experience":
    raise RuntimeError(
        "O objeto transferido não é um nó do tipo experience."
    )

print("Tipo da experiência:", experience_node.get("type"))
print(
    "Trajetória aprendida:",
    experience_node.get("data", {}).get("trajectory", [])
)

# ------------------------------------------------------------------
# FASE 1 — COLD START
# ------------------------------------------------------------------

print("\n[FASE 1] Cold Start — grafo limpo...")

graph_cold = build_problem_graph(
    "problem_shipping_tier",
    shipping_description,
    shipping_tests,
    "candidate_shipping_buggy",
    shipping_code,
)

engine_cold = ProblemEngine(
    graph_cold,
    "problem_shipping_tier",
)

res_cold = engine_cold.solve(
    generations=6,
    beam_width=5,
)

# ------------------------------------------------------------------
# FASE 2 — WARM START
# ------------------------------------------------------------------

print("\n[FASE 2] Warm Start — experiência transferida...")

graph_warm = build_problem_graph(
    "problem_shipping_tier",
    shipping_description,
    shipping_tests,
    "candidate_shipping_buggy",
    shipping_code,
)

# Copia o nó REAL da experiência, e não somente seu ID.
transferred_experience = dict(experience_node)
transferred_experience["id"] = "experience_transfer"

graph_warm.nodes["experience_transfer"] = transferred_experience

graph_warm.connect(
    "problem_shipping_tier",
    "experience_transfer",
    "has_experience",
)

engine_warm = ProblemEngine(
    graph_warm,
    "problem_shipping_tier",
)

res_warm = engine_warm.solve(
    generations=6,
    beam_width=5,
)

# ------------------------------------------------------------------
# MÉTRICAS
# ------------------------------------------------------------------

eval_cold = len(res_cold.get("evaluated_candidates", []))
eval_warm = len(res_warm.get("evaluated_candidates", []))

if eval_cold:
    reduction = ((eval_cold - eval_warm) / eval_cold) * 100
else:
    reduction = 0.0

print("\n" + "=" * 70)
print("RELATÓRIO COMPARATIVO")
print("=" * 70)

print(
    "Cold Start ->",
    "Sucesso:", res_cold.get("success"),
    "| Score:", res_cold.get("score"),
    "| Candidatos:", eval_cold,
)

print(
    "Warm Start ->",
    "Sucesso:", res_warm.get("success"),
    "| Score:", res_warm.get("score"),
    "| Candidatos:", eval_warm,
)

print(f"Redução de candidatos: {reduction:.2f}%")

print("Caminho Cold:", res_cold.get("path"))
print("Caminho Warm:", res_warm.get("path"))

print(
    "Experiência transferida:",
    graph_warm.nodes.get("experience_transfer", {}).get("type")
)

print("=" * 70)
