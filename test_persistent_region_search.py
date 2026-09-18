from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.path_search import PathSearch
from engine.context_memory import ContextMemory

SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""

TESTS = """
TEST: resolver(5, 2) == (3, 3)
"""

graph = Graph()

graph.add_node(
    "source",
    "code",
    {
        "code": SOURCE
    }
)

context = ContextMemory(graph)

context.remember(
    TESTS,
    [
        "binop_1_sub_to_add",
        "binop_0_add_to_sub",
    ],
    score=1.0,
    region_path=[
        (1, "BinOp"),
        (0, "BinOp"),
    ],
)

def evaluator(code):
    return {
        "success": False,
        "score": 0.0,
        "reason": "teste de prioridade persistente",
        "passed": 0,
        "total": 1,
    }

search = PathSearch(
    graph=graph,
    mutator=AutomaticASTMutator(),
    evaluator=evaluator,
    max_depth=1,
    beam_width=10,
    context_memory=context,
    context_tests=TESTS,
)

result = search.search("source")

evaluated = result["evaluated_candidates"]

print("ORDEM DA BUSCA:")
print()

for item in evaluated:
    print(
        item["candidate"],
        "| região:",
        item["region_index"],
        "| tipo:",
        item["region_type"],
    )

print()

assert evaluated

first = evaluated[0]

print(
    "PRIMEIRO:",
    first["candidate"],
    "| região:",
    first["region_index"],
    "| tipo:",
    first["region_type"],
)

assert first["candidate"] == "binop_1_sub_to_add"
assert first["region_index"] == 1
assert first["region_type"] == "BinOp"

print()
print("REGRA CORRETA: OK")
print("REGIÃO CORRETA: OK")
print("MEMÓRIA PERSISTENTE → PATHSEARCH: OK")
print("TESTE FINAL: OK")
