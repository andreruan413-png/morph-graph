from graph.core import Graph


FILE = "tests/graph_persistence_test.json"


print("=" * 50)
print("TESTE DE PERSISTÊNCIA DO GRAPH")
print("=" * 50)

# 1. Criar grafo original
graph = Graph()

graph.add_node(
    "problem",
    "problem",
    {"description": "teste de persistência"}
)

graph.add_node(
    "code",
    "code",
    {"code": "def solve(x): return x + 1"}
)

graph.connect(
    "problem",
    "code",
    "solved_by"
)

original = graph.snapshot()
original_hash = original["hash"]

print("GRAFO ORIGINAL")
print("Nós:", len(graph.nodes))
print("Conexões:", len(graph.edges))
print("Histórico:", len(graph.history))
print("Hash:", original_hash)

# 2. Salvar
graph.save(FILE)

print()
print("SALVAMENTO: OK")

# 3. Carregar usando Graph.load()
loaded = Graph.load(FILE)

print()
print("GRAFO CARREGADO")
print("Nós:", len(loaded.nodes))
print("Conexões:", len(loaded.edges))
print("Histórico:", len(loaded.history))

# 4. Verificar estrutura
assert loaded.nodes == graph.nodes
assert loaded.edges == graph.edges
assert loaded.history == graph.history

print()
print("ESTRUTURA: OK")

# 5. Verificar hash estrutural
loaded_snapshot = loaded.snapshot()
loaded_hash = loaded_snapshot["hash"]

print("Hash original :", original_hash)
print("Hash carregado :", loaded_hash)

assert original_hash == loaded_hash

print()
print("HASH: OK")

# 6. Verificar que o grafo continua utilizável
loaded.add_node(
    "after_reload",
    "test",
    {"message": "grafo continua funcionando"}
)

assert "after_reload" in loaded.nodes

print("GRAFO APÓS RELOAD: OPERACIONAL")

print()
print("=" * 50)
print("PERSISTÊNCIA DO GRAPH: TESTE FINAL: OK")
print("=" * 50)
