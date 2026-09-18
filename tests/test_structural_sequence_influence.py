from graph.core import Graph
from engine.auto_mutation import MutationCandidate
from engine.path_search import PathSearch


def make_candidate(name, region_index, region_type, mutation_type):
    return MutationCandidate(
        name=name,
        tree=None,
        region_index=region_index,
        region_type=region_type,
        mutation_type=mutation_type,
    )


class FakeMutator:
    def generate(self, code):
        return [
            make_candidate(
                "new_operator",
                1,
                "BinOp",
                "operator_change",
            ),
            make_candidate(
                "new_operand",
                1,
                "BinOp",
                "operand_swap",
            ),
        ]


def fake_evaluator(code):
    return {
        "success": False,
        "score": 0.0,
        "reason": "teste estrutural",
    }


graph = Graph()

graph.add_node(
    "problem_structural",
    "problem",
    {"description": "teste"},
)

graph.add_node(
    "source",
    "code",
    {"code": "x = a + b"},
)

graph.connect(
    "problem_structural",
    "source",
    "has_candidate",
)

# Experiência anterior:
#
# old_operator tem exatamente a mesma estrutura
# de new_operator.
#
# O nome é diferente propositalmente.
graph.add_node(
    "decision_old",
    "decision",
    {
        "problem_id": "problem_structural",
        "candidate": "old_operator",
        "region_index": 1,
        "region_type": "BinOp",
        "mutation_type": "operator_change",
        "path": [],
        "useful": True,
    },
)

graph.add_node(
    "decision_old_other",
    "decision",
    {
        "problem_id": "problem_structural",
        "candidate": "old_other",
        "region_index": 1,
        "region_type": "BinOp",
        "mutation_type": "operand_swap",
        "path": [],
        "useful": False,
    },
)

search = PathSearch(
    graph=graph,
    mutator=FakeMutator(),
    evaluator=fake_evaluator,
    max_depth=1,
    beam_width=2,
    use_trajectory=False,
    use_structure=False,
    use_graph_guidance=False,
    use_context_guidance=False,
    use_failure_guidance=False,
    use_decision_score=True,
)

search._current_code = "x = a + b"

candidates = FakeMutator().generate("x = a + b")

scores = []

for candidate in candidates:
    score = search._decision_score_for_candidate(
        [],
        candidate,
    )
    scores.append((candidate.name, score.as_dict()))

print("=== SCORES ESTRUTURAIS ===")

for name, score in scores:
    print(
        name,
        "=>",
        "sequence:",
        score["sequence_learning"],
        "| structural:",
        score["structural_sequence"],
        "| total:",
        score["total"],
    )

operator_score = scores[0][1]
operand_score = scores[1][1]

assert operator_score["structural_sequence"] > 0.0
assert operand_score["structural_sequence"] > 0.0
assert operator_score["structural_sequence"] > operand_score["structural_sequence"]
assert operator_score["total"] > operand_score["total"]

print()
print("TRANSFERÊNCIA ESTRUTURAL → OK")
print("NOMES DIFERENTES → OK")
print("ESTRUTURA INFLUENCIOU O DECISION SCORE → OK")
