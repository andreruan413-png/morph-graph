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
"""

add_code_node(
    graph,
    "code_001",
    original_code,
    {
        "description": "programa inicial"
    }
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


print("=== CÓDIGO ORIGINAL ===")
print(original_code)


for index, rule in enumerate(rules, start=2):

    node_id = f"code_{index:03d}"

    print(f"\n=== TESTANDO {rule.name} ===")

    node = rule.transform(
        graph,
        "code_001",
        node_id
    )

    verification = verify_python_code(
        node["data"]["code"]
    )

    evaluation = Evaluation(
        verification.success,
        verification.score,
        verification.reason
    )

    evaluation_id = record_evaluation(
        graph,
        node_id,
        evaluation
    )

    print("Resultado:")
    print(evaluation.as_dict())


print("\n=== RESULTADOS ===")

for node_id, node in graph.nodes.items():

    if node["type"] != "evaluation":
        continue

    data = node["data"]

    target = data["target_node"]

    rule = graph.nodes[target]["data"].get(
        "generated_by"
    )

    print({
        "rule": rule,
        "target": target,
        "score": data["score"],
        "success": data["success"]
    })


print("\n=== GRAFO ===")

print(graph.snapshot())
