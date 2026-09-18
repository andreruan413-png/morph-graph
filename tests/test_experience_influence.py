from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine


SOURCE_TESTS = """
TEST: assert calculate_tiered_revenue(100, 5, 2, 10) == 100
TEST: assert calculate_tiered_revenue(200, 10, 3, 25) == 195
TEST: assert calculate_tiered_revenue(50, 2, 4, 5) == 47
"""

SOURCE_CODE = """
def calculate_tiered_revenue(base_fee, volume, bonus_factor, penalty):
    step1 = base_fee + (volume * bonus_factor)
    total = step1 * penalty
    return total
"""

SHIPPING_DESCRIPTION = """
Corrija a função calculate_shipping_tier.
A regra correta é:
subtotal = base_cost - (distance * weight_factor)
total = subtotal + handling_fee
"""

SHIPPING_TESTS = """
TEST: assert calculate_shipping_tier(100, 5, 2, 10) == 100
TEST: assert calculate_shipping_tier(200, 10, 3, 25) == 195
TEST: assert calculate_shipping_tier(50, 2, 4, 5) == 47
"""

SHIPPING_CODE = """
def calculate_shipping_tier(base_cost, distance, weight_factor, handling_fee):
    subtotal = base_cost + (distance * weight_factor)
    total = subtotal * handling_fee
    return total
"""


def build_graph(problem_id, description, tests, candidate_id, code):
    graph = Graph()
    problem = Problem(problem_id, description, tests)
    problem.add_to_graph(graph)
    add_code_node(graph, candidate_id, code)
    graph.connect(problem_id, candidate_id, "has_candidate")
    return graph


def decision_nodes(graph):
    result = []

    for node_id, node in graph.nodes.items():
        if not isinstance(node, dict):
            continue

        if node.get("type") != "decision":
            continue

        data = node.get("data", {})

        result.append({
            "id": node_id,
            "candidate": data.get("candidate"),
            "selected": data.get("selected"),
            "path": data.get("path"),
            "scores": data.get("scores"),
            "rule": data.get("candidate"),
            "mutation_type": data.get("mutation_type"),
            "region_index": data.get("region_index"),
        })

    return result


print("=" * 70)
print("MORPH-GRAPH — TESTE DE INFLUÊNCIA DA EXPERIÊNCIA")
print("=" * 70)

# ------------------------------------------------------------
# 1. PRODUZIR EXPERIÊNCIA ANTERIOR
# ------------------------------------------------------------

source_graph = build_graph(
    "problem_multi_step",
    "Problema anterior",
    SOURCE_TESTS,
    "candidate_multi_step_buggy",
    SOURCE_CODE,
)

source_engine = ProblemEngine(
    source_graph,
    "problem_multi_step",
)

source_result = source_engine.solve(
    generations=6,
    beam_width=5,
)

experience_id = source_result.get("experience_node")

if not experience_id:
    raise RuntimeError("Experiência de origem não foi produzida.")

experience = source_graph.nodes[experience_id]

print("\nExperiência:", experience_id)
print(
    "Trajetória:",
    experience.get("data", {}).get("trajectory", [])
)

# ------------------------------------------------------------
# 2. CASO A — SEM EXPERIÊNCIA
# ------------------------------------------------------------

cold_graph = build_graph(
    "problem_shipping_tier",
    SHIPPING_DESCRIPTION,
    SHIPPING_TESTS,
    "candidate_shipping_buggy",
    SHIPPING_CODE,
)

cold_engine = ProblemEngine(
    cold_graph,
    "problem_shipping_tier",
)

cold = cold_engine.solve(
    generations=6,
    beam_width=5,
)

cold_decisions = decision_nodes(cold_graph)

# ------------------------------------------------------------
# 3. CASO B — COM EXPERIÊNCIA
# ------------------------------------------------------------

warm_graph = build_graph(
    "problem_shipping_tier",
    SHIPPING_DESCRIPTION,
    SHIPPING_TESTS,
    "candidate_shipping_buggy",
    SHIPPING_CODE,
)

transferred = dict(experience)
transferred["id"] = "experience_transfer"

warm_graph.nodes["experience_transfer"] = transferred

warm_graph.connect(
    "problem_shipping_tier",
    "experience_transfer",
    "has_experience",
)

warm_engine = ProblemEngine(
    warm_graph,
    "problem_shipping_tier",
)

warm = warm_engine.solve(
    generations=6,
    beam_width=5,
)

warm_decisions = decision_nodes(warm_graph)

# ------------------------------------------------------------
# 4. COMPARAÇÃO
# ------------------------------------------------------------

cold_count = len(cold.get("evaluated_candidates", []))
warm_count = len(warm.get("evaluated_candidates", []))

print("\n" + "=" * 70)
print("RESULTADO")
print("=" * 70)

print("\nCOLD START")
print("Sucesso:", cold.get("success"))
print("Score:", cold.get("score"))
print("Candidatos:", cold_count)
print("Caminho:", cold.get("path"))
print("Decisões no grafo:", len(cold_decisions))

print("\nWARM START")
print("Sucesso:", warm.get("success"))
print("Score:", warm.get("score"))
print("Candidatos:", warm_count)
print("Caminho:", warm.get("path"))
print("Decisões no grafo:", len(warm_decisions))

if cold_count:
    reduction = ((cold_count - warm_count) / cold_count) * 100
else:
    reduction = 0.0

print("\nRedução de candidatos:", f"{reduction:.2f}%")

print("\nPRIMEIRAS DECISÕES — COLD")
for item in cold_decisions[:10]:
    print(item)

print("\nPRIMEIRAS DECISÕES — WARM")
for item in warm_decisions[:10]:
    print(item)

print("\n" + "=" * 70)
