from graph.core import Graph
from engine.context_memory import ContextMemory


FILE = "tests/context_persistence_test.json"

print("=" * 60)
print("TESTE DE PERSISTÊNCIA DA MEMÓRIA CONTEXTUAL")
print("=" * 60)

# --------------------------------------------------
# 1. Criar grafo
# --------------------------------------------------

graph = Graph()

graph.add_node(
    "problem",
    "problem",
    {
        "description": "problema aritmético"
    }
)

graph.add_node(
    "experience",
    "experience",
    {
        "problem_id": "problem",
        "solution_node": "solution",
        "score": 1.0,
        "trajectory": [
            {
                "rule": "binop_1_sub_to_add",
                "region_index": 1,
                "region_type": "BinOp"
            },
            {
                "rule": "binop_0_add_to_sub",
                "region_index": 0,
                "region_type": "BinOp"
            }
        ]
    }
)

graph.connect(
    "problem",
    "experience",
    "produced_experience"
)

# --------------------------------------------------
# 2. Contexto original
# --------------------------------------------------

tests = """
TEST: solve(5, 3) == 8
TEST: solve(10, 4) == 14
"""

memory = ContextMemory(graph)

original_profile = memory.context_profile(tests)

print()
print("PERFIL ORIGINAL:")
print(original_profile)

assert original_profile
assert original_profile == [
    ("a+b",),
    ("a+b",),
]

print("PERFIL ORIGINAL: OK")

# --------------------------------------------------
# 3. Salvar
# --------------------------------------------------

graph.save(FILE)

print()
print("GRAFO SALVO: OK")

# --------------------------------------------------
# 4. Destruir objeto original
# --------------------------------------------------

del memory
del graph

# --------------------------------------------------
# 5. Recarregar do disco
# --------------------------------------------------

loaded_graph = Graph.load(FILE)

print()
print("GRAFO RECARREGADO:")
print("Nós:", len(loaded_graph.nodes))
print("Conexões:", len(loaded_graph.edges))
print("Histórico:", len(loaded_graph.history))

assert "problem" in loaded_graph.nodes
assert "experience" in loaded_graph.nodes

print("ESTRUTURA RECARREGADA: OK")

# --------------------------------------------------
# 6. Reconstruir ContextMemory usando o grafo
#    RECUPERADO
# --------------------------------------------------

loaded_memory = ContextMemory(loaded_graph)

loaded_profile = loaded_memory.context_profile(tests)

print()
print("PERFIL APÓS RELOAD:")
print(loaded_profile)

# --------------------------------------------------
# 7. Comparação
# --------------------------------------------------

assert loaded_profile == original_profile

print("PERFIL CONTEXTUAL PERSISTENTE: OK")

# --------------------------------------------------
# 8. Verificar que a experiência continua no grafo
# --------------------------------------------------

experience = loaded_graph.nodes["experience"]

assert experience["data"]["score"] == 1.0
assert experience["data"]["trajectory"]

trajectory = experience["data"]["trajectory"]

assert trajectory[0]["rule"] == "binop_1_sub_to_add"
assert trajectory[0]["region_index"] == 1
assert trajectory[0]["region_type"] == "BinOp"

assert trajectory[1]["rule"] == "binop_0_add_to_sub"
assert trajectory[1]["region_index"] == 0
assert trajectory[1]["region_type"] == "BinOp"

print("TRAJETÓRIA PERSISTENTE: OK")
print("REGIÕES PERSISTENTES: OK")

print()
print("=" * 60)
print("MEMÓRIA CONTEXTUAL: TESTE FINAL: OK")
print("=" * 60)
