from graph.core import Graph
from engine.code_node import add_code_node
from engine.verifier import verify_python_code
from engine.evaluator import Evaluation, record_evaluation


graph = Graph()

code = """
def soma(a, b):
    return a + b

assert soma(2, 3) == 5

print("CÓDIGO FUNCIONOU")
"""

print("=== CRIANDO NÓ DE CÓDIGO ===")

node = add_code_node(
    graph,
    "code_001",
    code,
    {
        "description": "primeiro programa executável"
    }
)

print(node)


print("\n=== VERIFICANDO CÓDIGO ===")

verification = verify_python_code(
    node["data"]["code"]
)

print(verification.as_dict())


print("\n=== REGISTRANDO AVALIAÇÃO ===")

evaluation = Evaluation(
    verification.success,
    verification.score,
    verification.reason
)

evaluation_id = record_evaluation(
    graph,
    node["id"],
    evaluation
)

print(graph.nodes[evaluation_id])


print("\n=== GRAFO FINAL ===")

print(graph.snapshot())
