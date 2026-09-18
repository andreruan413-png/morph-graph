from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node
from engine.problem_engine import ProblemEngine


TESTS = """
TEST: assert calculate_shipping_tier(100, 5, 2, 10) == 100
TEST: assert calculate_shipping_tier(200, 10, 3, 25) == 195
TEST: assert calculate_shipping_tier(50, 2, 4, 5) == 47
"""

CODE = """
def calculate_shipping_tier(base_cost, distance, weight_factor, handling_fee):
    subtotal = base_cost + (distance * weight_factor)
    total = subtotal * handling_fee
    return total
"""


def build_graph():
    graph = Graph()

    problem = Problem(
        "problem_memory_negative",
        """
        Corrija calculate_shipping_tier.
        A regra correta é:
        subtotal = base_cost - (distance * weight_factor)
        total = subtotal + handling_fee
        """,
        TESTS,
    )

    problem.add_to_graph(graph)

    add_code_node(
        graph,
        "candidate_shipping_buggy",
        CODE,
    )

    graph.connect(
        "problem_memory_negative",
        "candidate_shipping_buggy",
        "has_candidate",
    )

    return graph


def run(label, graph):
    engine = ProblemEngine(
        graph,
        "problem_memory_negative",
    )

    result = engine.solve(
        generations=6,
        beam_width=5,
    )

    decisions = []

    for node_id, node in graph.nodes.items():
        if not isinstance(node, dict):
            continue

        if node.get("type") != "decision":
            continue

        data = node.get("data", {})
        scores = data.get("scores", {})

        decisions.append({
            "id": node_id,
            "candidate": data.get("candidate"),
            "selected": data.get("selected"),
            "path": data.get("path"),
            "total": scores.get("total"),
            "context": scores.get("context"),
            "trajectory": scores.get("trajectory"),
            "graph": scores.get("graph"),
            "learned": scores.get("learned"),
        })

    print(f"\n--- {label} ---")
    print("Sucesso:", result.get("success"))
    print("Score:", result.get("score"))
    print("Candidatos:", len(result.get("evaluated_candidates", [])))
    print("Caminho:", result.get("path"))
    print("Decisões:", len(decisions))

    print("Primeiras 10 decisões:")
    for decision in decisions[:10]:
        print(decision)

    return result, decisions


print("=" * 70)
print("MORPH-GRAPH — CONTROLE NEGATIVO DA MEMÓRIA")
print("=" * 70)

# CONTROLE: nenhum conhecimento anterior.
control_graph = build_graph()

# TESTE: experiência irrelevante para o problema atual.
negative_graph = build_graph()

irrelevant_experience = {
    "id": "experience_irrelevant",
    "type": "experience",
    "data": {
        "problem_id": "unrelated_problem",
        "solution_node": "unrelated_solution",
        "source_code": """
def completely_unrelated(x):
    return x * 100 + 7
""",
        "score": 1.0,
        "generations": [
            {
                "generation": 1,
                "source": "unrelated_problem",
                "selected": {
                    "rule": "binop_0_add_to_mult",
                    "node_id": None,
                    "score": 1.0,
                    "region_index": 0,
                    "region_type": "BinOp",
                },
            }
        ],
        "trajectory": [
            {
                "rule": "binop_0_add_to_mult",
                "region_index": 0,
                "region_type": "BinOp",
            }
        ],
    },
}

negative_graph.nodes["experience_irrelevant"] = irrelevant_experience

negative_graph.connect(
    "problem_memory_negative",
    "experience_irrelevant",
    "has_experience",
)

control_result, control_decisions = run(
    "CONTROLE — SEM MEMÓRIA",
    control_graph,
)

negative_result, negative_decisions = run(
    "CONTROLE NEGATIVO — MEMÓRIA IRRELEVANTE",
    negative_graph,
)

print("\n" + "=" * 70)
print("COMPARAÇÃO")
print("=" * 70)

print(
    "Candidatos sem memória:",
    len(control_result.get("evaluated_candidates", [])),
)

print(
    "Candidatos com memória irrelevante:",
    len(negative_result.get("evaluated_candidates", [])),
)

print(
    "Caminho sem memória:",
    control_result.get("path"),
)

print(
    "Caminho com memória irrelevante:",
    negative_result.get("path"),
)

if control_decisions and negative_decisions:
    print("\nPRIMEIRA DECISÃO — CONTROLE")
    print(control_decisions[0])

    print("\nPRIMEIRA DECISÃO — MEMÓRIA IRRELEVANTE")
    print(negative_decisions[0])

print("\n" + "=" * 70)
print("FIM DO CONTROLE NEGATIVO")
print("=" * 70)
