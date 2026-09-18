import json
import os

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

GRAPH_FILE = "graph_persistence_test.json"

# ============================================================
# 1. CRIA MEMÓRIA E APRENDE A TRAJETÓRIA
# ============================================================

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

print("TRAJETÓRIA APRENDIDA:")
print(
    context.trajectories_for(TESTS)
)

# ============================================================
# 2. SALVA EM DISCO
# ============================================================

graph.save(GRAPH_FILE)

assert os.path.exists(GRAPH_FILE)

print()
print("GRAFO SALVO EM DISCO: OK")

# ============================================================
# 3. DESTRÓI O GRAFO ORIGINAL
# ============================================================

del graph
del context

# ============================================================
# 4. CARREGA O ARQUIVO DO DISCO
# ============================================================

with open(
    GRAPH_FILE,
    "r",
    encoding="utf-8",
) as f:
    saved = json.load(f)

loaded_graph = Graph()

loaded_graph.nodes = saved["nodes"]
loaded_graph.edges = saved["edges"]
loaded_graph.history = saved["history"]

print("GRAFO RECARREGADO: OK")

# ============================================================
# 5. RECRIA A MEMÓRIA A PARTIR DO GRAFO RECARREGADO
# ============================================================

loaded_context = ContextMemory(
    loaded_graph
)

trajectories = (
    loaded_context.trajectories_for(
        TESTS
    )
)

print()
print("TRAJETÓRIA APÓS RECARREGAR:")
print(trajectories)

assert trajectories

path = trajectories[0]["path"]

assert path == [
    "binop_1_sub_to_add",
    "binop_0_add_to_sub",
]

region_path = trajectories[0].get(
    "region_path",
    []
)

assert region_path == [
    {
        "region_index": 1,
        "region_type": "BinOp",
    },
    {
        "region_index": 0,
        "region_type": "BinOp",
    },
]

print()
print("TRAJETÓRIA PERSISTENTE: OK")
print("REGIÕES PERSISTENTES: OK")

# ============================================================
# 6. TESTA O PATHSEARCH USANDO SOMENTE A MEMÓRIA RECARREGADA
# ============================================================

def evaluator(code):
    return {
        "success": False,
        "score": 0.0,
        "reason": "teste de persistência em disco",
        "passed": 0,
        "total": 1,
    }

search = PathSearch(
    graph=loaded_graph,
    mutator=AutomaticASTMutator(),
    evaluator=evaluator,
    max_depth=1,
    beam_width=10,
    context_memory=loaded_context,
    context_tests=TESTS,
)

result = search.search("source")

evaluated = result["evaluated_candidates"]

assert evaluated

first = evaluated[0]

print()
print("PRIMEIRO CANDIDATO APÓS RECARREGAR:")
print(
    first["candidate"],
    "| região:",
    first["region_index"],
    "| tipo:",
    first["region_type"],
)

assert first["candidate"] == (
    "binop_1_sub_to_add"
)

assert first["region_index"] == 1

assert first["region_type"] == "BinOp"

print()
print("PATHSEARCH APÓS RECARREGAR: OK")
print("REGRA PERSISTENTE: OK")
print("REGIÃO PERSISTENTE: OK")
print()
print("========================================")
print("PERSISTÊNCIA EM DISCO: TESTE FINAL: OK")
print("========================================")
