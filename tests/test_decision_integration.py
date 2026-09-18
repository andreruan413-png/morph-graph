from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.path_search import PathSearch


def evaluator(code):
    if "return a - b" in code:
        return {
            "success": True,
            "score": 1.0,
            "reason": "solução correta",
        }

    return {
        "success": False,
        "score": 0.0,
        "reason": "solução incorreta",
    }


graph = Graph()

source_code = """
def resolver(a, b):
    return a + b
"""

graph.add_node(
    "problem_001",
    "problem",
    {"description": "resolver a - b"},
)

graph.add_node(
    "source_001",
    "code",
    {
        "code": source_code,
        "language": "python",
    },
)

graph.connect(
    "problem_001",
    "source_001",
    "has_candidate",
)

mutator = AutomaticASTMutator()

search = PathSearch(
    graph=graph,
    mutator=mutator,
    evaluator=evaluator,
    max_depth=2,
    beam_width=3,
    use_trajectory=True,
    use_structure=True,
    use_pruner=False,
    use_graph_guidance=True,
    use_context_guidance=True,
    use_failure_guidance=True,
    use_decision_score=True,
)

result = search.search(
    source_id="source_001",
)

print("=== DECISION SCORE INTEGRATION ===")
print("Sucesso:", result.get("success"))
print("Score:", result.get("score"))
print("Caminho:", result.get("path"))
print("Nó final:", result.get("node_id"))

assert result.get("success") is True
assert result.get("score") >= 1.0

print("DECISION SCORE → PATHSEARCH: OK")
print("PATHSEARCH → SOLUÇÃO: OK")
