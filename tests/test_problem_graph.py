from graph.core import Graph
from engine.problem import Problem
from engine.code_node import add_code_node


print("========================================")
print(" MORPH-GRAPH - PROBLEMA NO GRAFO")
print("========================================")


graph = Graph()


problem = Problem(
    problem_id="problem_001",

    description=(
        "Criar uma função calcular "
        "que some dois números."
    ),

    tests="""
TEST: assert candidate.calcular(2, 3) == 5
TEST: assert candidate.calcular(10, 7) == 17
"""
)


problem.add_to_graph(
    graph
)


code = """
def calcular(a, b):
    return a + b
"""


add_code_node(
    graph,
    "candidate_001",
    code,
    {
        "problem_id": "problem_001",
        "role": "candidate"
    }
)


graph.connect(
    "problem_001",
    "candidate_001",
    "has_candidate"
)


print("\n=== NÓS ===")

for node_id, node in graph.nodes.items():

    print(
        node_id,
        "|",
        node["type"]
    )


print("\n=== CONEXÕES ===")

for edge in graph.edges:

    print(
        edge["source"],
        "--[",
        edge["relation"],
        "]-->",
        edge["target"]
    )


print("\n=== PROBLEMA ===")

print(
    graph.nodes[
        "problem_001"
    ]
)


print("\n=== TESTES ===")

print(
    graph.nodes[
        "problem_001_tests"
    ]["data"]["content"]
)


print("\n=== CANDIDATO ===")

print(
    graph.nodes[
        "candidate_001"
    ]["data"]["code"]
)


print("\n========================================")
print(" FIM DO TESTE")
print("========================================")

