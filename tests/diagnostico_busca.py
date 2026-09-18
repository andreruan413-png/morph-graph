from graph.core import Graph
from engine.code_node import add_code_node
from engine.evolution import EvolutionEngine

TESTS = """
TEST: solve(10, 3, 2) == 5
TEST: solve(20, 7, 4) == 9
TEST: solve(8, 2, 3) == 9
TEST: solve(15, 5, 1) == 11
"""

graph = Graph()

add_code_node(
    graph,
    "source",
    """
def solve(a, b, c):
    return (a + b) - c
""".strip(),
)

engine = EvolutionEngine(graph, tests=TESTS)

frontier = ["source"]

for generation in range(1, 4):

    print()
    print("=" * 70)
    print(f"GERAÇÃO {generation}")
    print("=" * 70)

    next_frontier = []

    for node_id in frontier:

        node = graph.nodes[node_id]
        code = node["data"]["code"]

        print()
        print(f"ORIGEM: {node_id}")
        print(code)

        candidates = engine.generate_candidates(node_id)

        print()
        print(f"CANDIDATOS: {len(candidates)}")

        for candidate in candidates:

            candidate_code = candidate.code()

            if candidate_code == code:
                continue

            result = engine.evaluate_candidate(
                node_id,
                candidate,
            )

            print()
            print(
                f"{candidate.name} | "
                f"score={result['score']} | "
                f"node={result['node_id']}"
            )

            print(candidate_code)

            if (
                result["node_id"]
                and result["score"] > 0
            ):
                next_frontier.append(
                    result["node_id"]
                )

            if result["score"] >= 1.0:
                print()
                print("!!! SOLUÇÃO ENCONTRADA !!!")
                raise SystemExit

    frontier = list(dict.fromkeys(next_frontier))

    print()
    print("PRÓXIMA FRONTEIRA:")
    print(frontier)

    if not frontier:
        print("FRONTEIRA VAZIA")
        break

print()
print("=" * 70)
print("DIAGNÓSTICO FINAL")
print("=" * 70)
