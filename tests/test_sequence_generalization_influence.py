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
        key=lambda candidate:
            search._candidate_sort_key(
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
print("MORPH-GRAPH — INFLUÊNCIA DA GENERALIZAÇÃO NA DECISÃO")
print("=" * 70)

graph = FakeGraph()

search = make_search(graph)

# ------------------------------------------------------------
# CANDIDATOS
# ------------------------------------------------------------

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
# 1. SEM MEMÓRIA
# ------------------------------------------------------------

search.sequence_learning = ZeroSequenceLearning()

without_learning = rank(
    search,
    ["A", "X"],
    candidates,
)

print()
print("SEM GENERALIZAÇÃO")

for name, scores in without_learning:
    print(
        name,
        "=> total:",
        scores["total"],
        "| sequence:",
        scores["sequence_learning"],
    )

assert without_learning[0][0] == "A"

# ------------------------------------------------------------
# 2. EXPERIÊNCIA ANTERIOR
# ------------------------------------------------------------
#
# O sistema já viu:
#
# [A, B] -> B
#
# Mas agora está diante de:
#
# [A, X]
#
# A sequência atual nunca apareceu antes.
#

graph.nodes["decision_sequence_generalized"] = {
    "id": "decision_sequence_generalized",
    "type": "decision",
    "data": {
        "path": ["A", "B"],
        "candidate": "B",
        "useful": True,
    },
}

search.sequence_learning = SequenceLearning(graph)

# ------------------------------------------------------------
# 3. DECISÃO COM GENERALIZAÇÃO
# ------------------------------------------------------------

with_learning = rank(
    search,
    ["A", "X"],
    candidates,
)

print()
print("COM GENERALIZAÇÃO")

for name, scores in with_learning:
    print(
        name,
        "=> total:",
        scores["total"],
        "| sequence:",
        scores["sequence_learning"],
    )

without_names = [
    name
    for name, _ in without_learning
]

with_names = [
    name
    for name, _ in with_learning
]

print()
print(
    "Contexto atual:",
    ["A", "X"],
)

print(
    "Experiência armazenada:",
    ["A", "B"],
    "-> B",
)

print(
    "Ordem sem generalização:",
    without_names,
)

print(
    "Ordem com generalização:",
    with_names,
)

# ------------------------------------------------------------
# 4. PROVAS
# ------------------------------------------------------------

generalized_b_score = next(
    scores["sequence_learning"]
    for name, scores in with_learning
    if name == "B"
)

generalized_a_score = next(
    scores["sequence_learning"]
    for name, scores in with_learning
    if name == "A"
)

assert generalized_b_score == 0.5

assert generalized_a_score == 0.0

assert with_learning[0][0] == "B"

assert without_names != with_names

print()
print(
    "EVIDÊNCIA TRANSFERIDA DE SEQUÊNCIA SEMELHANTE → OK"
)

print(
    "GENERALIZAÇÃO ENTROU NO DECISION SCORE → OK"
)

print(
    "GENERALIZAÇÃO ALTEROU A ORDEM DA DECISÃO → OK"
)

print()
print("=" * 70)
print("INTEGRAÇÃO DA GENERALIZAÇÃO → OK")
print("=" * 70)
