import ast

from graph.core import Graph
from engine.code_node import add_code_node
from engine.ast_mutation import ASTMutationRule


graph = Graph()

code = """
def soma(a,b):
    return a + b

assert soma(2,3)==5
"""

add_code_node(
    graph,
    "code_001",
    code
)

rule = ASTMutationRule(
    "plus_to_minus",
    ast.Add,
    ast.Sub
)

result = rule.transform(
    graph,
    "code_001",
    "code_002"
)

print("=== ORIGINAL ===")
print(code)

print("\n=== MUTADO ===")
print(result["data"]["code"])
