from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine


TESTS = """
TEST: solve(10, 3, 2) == 9
TEST: solve(20, 7, 4) == 17
TEST: solve(8, 2, 3) == 9
TEST: solve(15, 5, 1) == 11
"""


def create_graph():
    graph = Graph()

    add_code_node(
        graph,
        "source",
        """
def solve(a, b, c):
    return (a + b) - c
""".strip(),
    )

    return graph


print("=" * 70)
print("BENCHMARK: CAMINHO COM ESTADO NÃO MELHORANTE")
print("=" * 70)

# --------------------------------------------------
# 1. EVOLUTION ANTIGO
# --------------------------------------------------

graph_old = create_graph()

old_engine = EvolutionEngine(
    graph_old,
    tests=TESTS,
)

old_result = old_engine.evolve(
    "source",
    generations=5,
)

print()
print("=== HILL-CLIMBING ORIGINAL ===")
print("Sucesso:", old_result.get("success"))
print("Score:", old_result.get("final_score"))
print("Nó final:", old_result.get("final_node"))

# --------------------------------------------------
# 2. NOVA BUSCA COM EXPLORAÇÃO
# --------------------------------------------------

graph_new = create_graph()

new_engine = EvolutionEngine(
    graph_new,
    tests=TESTS,
)

new_result = new_engine.evolve_with_exploration(
    "source",
    generations=5,
    allow_non_improving=True,
    max_states=50,
)

print()
print("=== BUSCA COM EXPLORAÇÃO ===")
print("Sucesso:", new_result.get("success"))
print("Score:", new_result.get("final_score"))
print("Nó final:", new_result.get("final_node"))
print("Estados explorados:", new_result.get("states_explored"))
print("Caminho:", new_result.get("path"))

# --------------------------------------------------
# 3. VERIFICAÇÃO REAL
# --------------------------------------------------

assert new_result["success"] is True
assert new_result["final_score"] == 1.0

final_node = graph_new.nodes[
    new_result["final_node"]
]

final_code = final_node["data"]["code"]

print()
print("=== SOLUÇÃO ENCONTRADA ===")
print(final_code)

assert "return a - b + c" in final_code

# --------------------------------------------------
# 4. VERIFICAR QUE HOUVE MAIS DE UM PASSO
# --------------------------------------------------

path = new_result["path"]

assert len(path) >= 2

print()
print("=== TRAJETÓRIA ===")

for index, rule in enumerate(path, start=1):
    print(f"{index}. {rule}")

# --------------------------------------------------
# 5. COMPARAÇÃO
# --------------------------------------------------

print()
print("=" * 70)
print("RESULTADO")
print("=" * 70)

print(
    "Hill-climbing resolveu:",
    old_result.get("success"),
)

print(
    "Exploração resolveu:",
    new_result.get("success"),
)

print(
    "Estados explorados:",
    new_result.get("states_explored"),
)

if (
    old_result.get("success") is False
    and new_result.get("success") is True
):
    print()
    print("NOVO MOTOR SUPEROU O HILL-CLIMBING: OK")
elif new_result.get("success") is True:
    print()
    print("EXPLORAÇÃO FUNCIONAL: OK")
    print(
        "Observação: o hill-climbing também encontrou "
        "uma solução neste caso."
    )
else:
    raise AssertionError(
        "A busca com exploração não encontrou a solução."
    )

print("=" * 70)
