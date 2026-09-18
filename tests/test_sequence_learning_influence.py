from engine.path_search import PathSearch
from engine.sequence_learning import SequenceLearning


class Candidate:
    def __init__(self, name, region_index=0, region_type="binop"):
        self.name = name
        self.region_index = region_index
        self.region_type = region_type


class ZeroGuidance:
    def score_candidate(self, *args, **kwargs):
        return 0.0

    def candidate_score(self, *args, **kwargs):
        return 0.0

    def priorities(self, *args, **kwargs):
        return {}

    def mutation_priority(self, *args, **kwargs):
        return {}


class ZeroContextDecisionLearning:
    def score(self, *args, **kwargs):
        return 0.0


class ZeroCandidateLearning:
    def score_candidate(self, *args, **kwargs):
        return 0.0


class ZeroSequenceLearning:
    def score_structural(self, path_signatures, candidate_signature):
        return 0.0

    def score(self, path, candidate):
        return 0.0


def make_search(graph):
    search = PathSearch(
        graph=graph,
        mutator=None,
        evaluator=None,
        max_depth=1,
        beam_width=2,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        use_graph_guidance=False,
        use_context_guidance=False,
        use_failure_guidance=False,
        use_decision_score=True,
    )

    search._current_code = (
        "def resolver(a, b):\n"
        "    return a + b\n"
    )

    search.transition_memory = ZeroGuidance()
    search.trajectory_guidance = ZeroGuidance()
    search.graph_guidance = ZeroGuidance()
    search.context_guidance = ZeroGuidance()
    search.failure_guidance = ZeroGuidance()
    search.context_decision_learning = (
        ZeroContextDecisionLearning()
    )
    search.candidate_learning = ZeroCandidateLearning()

    return search


def rank(search, path, candidates):
    ranked = sorted(
        candidates,
        key=lambda candidate: search._candidate_sort_key(
            path,
            candidate,
        ),
        reverse=True,
    )

    return [
        (
            candidate.name,
            search._decision_score_for_candidate(
                path,
                candidate,
            ).as_dict(),
        )
        for candidate in ranked
    ]


class FakeGraph:
    def __init__(self):
        self.nodes = {}


print()
print("=" * 70)
print("MORPH-GRAPH — INFLUÊNCIA REAL DO SEQUENCE LEARNING")
print("=" * 70)

graph = FakeGraph()
search = make_search(graph)

# A começa com uma pequena vantagem estrutural.
# B começa atrás.
candidate_a = Candidate(
    "A",
    region_index=1,
)

candidate_b = Candidate(
    "B",
    region_index=0,
)

candidates = [
    candidate_a,
    candidate_b,
]

# ------------------------------------------------------------
# 1. SEM SEQUENCE LEARNING
# ------------------------------------------------------------

search.sequence_learning = ZeroSequenceLearning()

without_sequence = rank(
    search,
    [],
    candidates,
)

print()
print("SEM SEQUENCE LEARNING")

for name, scores in without_sequence:
    print(
        name,
        "=> total:",
        scores["total"],
        "| sequence:",
        scores["sequence_learning"],
    )

# Sem aprendizado, A deve vencer pelo desempate
# de region_index.
assert without_sequence[0][0] == "A"

# ------------------------------------------------------------
# 2. CRIANDO UMA EXPERIÊNCIA POSITIVA PARA B
# ------------------------------------------------------------

decision_id = "decision_sequence_test"

graph.nodes[decision_id] = {
    "id": decision_id,
    "type": "decision",
    "data": {
        "candidate": "B",
        "path": [],
        "useful": True,
    },
}

search.sequence_learning = SequenceLearning(graph)

with_sequence = rank(
    search,
    [],
    candidates,
)

print()
print("COM SEQUENCE LEARNING")

for name, scores in with_sequence:
    print(
        name,
        "=> total:",
        scores["total"],
        "| sequence:",
        scores["sequence_learning"],
    )

# ------------------------------------------------------------
# 3. PROVA DA MUDANÇA
# ------------------------------------------------------------

without_names = [
    name
    for name, _ in without_sequence
]

with_names = [
    name
    for name, _ in with_sequence
]

print()
print("Ordem sem aprendizado:", without_names)
print("Ordem com aprendizado:", with_names)

assert (
    with_sequence[0][1]["sequence_learning"]
    > without_sequence[0][1]["sequence_learning"]
)

assert with_sequence[0][0] == "B"

assert without_names != with_names

print()
print("SEQUENCE LEARNING ALTEROU A ORDEM → OK")
print("O efeito foi isolado dos demais sinais.")
print("TESTE DE INFLUENCIA CAUSAL → OK")
