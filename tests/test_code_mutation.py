from graph.core import Graph
from engine.code_node import add_code_node
from engine.code_mutation import CodeMutationRule
from engine.verifier import verify_python_code
from engine.evaluator import Evaluation, record_evaluation


graph = Graph()

original_code = """
def soma(a, b):
    return a + b

assert soma(2, 3) == 5

print("ORIGINAL PASSOU")
"""

add_code_node(
    graph,
    "code_001",
    original_code
)

rule = CodeMutationRule(
    "change_plus_to_minus",
    "return a + b",
    "return a - b"
)

print("=== APLICANDO MUTAÇÃO ===")

mutated = rule.transform(
    graph,
    "code_001",
    "code_002"
)

print(mutated)


print("\n=== VERIFICANDO CÓDIGO MUTADO ===")

verification = verify_python_code(
    mutated["data"]["code"]
)

print(verification.as_dict())


print("\n=== REGISTRANDO RESULTADO ===")

evaluation = Evaluation(
    verification.success,
    verification.score,
    verification.reason
)

evaluation_id = record_evaluation(
    graph,
    "code_002",
    evaluation
)

print(graph.nodes[evaluation_id])


print("\n=== COMPARAÇÃO ===")

print("Código original:")
print(graph.nodes["code_001"]["data"]["code"])

print("Código mutado:")
print(graph.nodes["code_002"]["data"]["code"])


print("\n=== HISTÓRICO ===")

for item in graph.history:
    print(item)
