from graph.core import Graph
from engine.code_node import add_code_node
from engine.code_mutation import CodeMutationRule
from engine.evolution import EvolutionEngine


graph = Graph()

original_code = """
def soma(a, b):
    return a + b

assert soma(2, 3) == 5
"""

add_code_node(
    graph,
    "code_001",
    original_code
)


rules = [
    CodeMutationRule(
        "change_plus_to_minus",
        "return a + b",
        "return a - b"
    ),

    CodeMutationRule(
        "change_plus_to_sum",
        "return a + b",
        "return b + a"
    )
]


engine = EvolutionEngine(graph)

candidates = []

print("=== GERANDO CANDIDATOS ===")

for rule in rules:
    result = engine.evaluate_candidate(
        "code_001",
        rule
    )

    candidates.append(result)

    print(result)


print("\n=== SELEÇÃO AUTOMÁTICA ===")

best = engine.choose_best(candidates)

print("MELHOR CANDIDATO:")
print(best)


print("\n=== DECISÃO DO MOTOR ===")

if best["success"]:
    print(
        f"O MORPH-GRAPH escolheu "
        f"{best['node_id']} usando a regra "
        f"'{best['rule']}'"
    )
else:
    print("Nenhum candidato passou na verificação.")
