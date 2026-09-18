from engine.sequence_learning import SequenceLearning


class FakeGraph:
    def __init__(self):
        self.nodes = {}


graph = FakeGraph()

learning = SequenceLearning(graph)

# Experiência aprendida anteriormente:
#
# [A, B] -> C
#
graph.nodes["decision_1"] = {
    "id": "decision_1",
    "type": "decision",
    "data": {
        "path": ["A", "B"],
        "candidate": "C",
        "useful": True,
    },
}

print()
print("=" * 70)
print("MORPH-GRAPH — GENERALIZAÇÃO DO SEQUENCE LEARNING")
print("=" * 70)

# ------------------------------------------------------------
# 1. SIMILARIDADE
# ------------------------------------------------------------

exact_similarity = learning.sequence_similarity(
    ["A", "B"],
    ["A", "B"],
)

similar_similarity = learning.sequence_similarity(
    ["A", "X"],
    ["A", "B"],
)

different_similarity = learning.sequence_similarity(
    ["X", "Y"],
    ["A", "B"],
)

print()
print("Similaridade exata:", exact_similarity)
print("Similaridade semelhante:", similar_similarity)
print("Similaridade diferente:", different_similarity)

assert exact_similarity == 1.0
assert similar_similarity == 0.5
assert different_similarity == 0.0

print("SIMILARIDADE ESTRUTURAL → OK")

# ------------------------------------------------------------
# 2. SEQUÊNCIA EXATA
# ------------------------------------------------------------

exact_score = learning.score(
    ["A", "B"],
    "C",
)

print()
print("Score sequência exata [A,B] -> C:", exact_score)

assert exact_score == 1.0

print("REUTILIZAÇÃO EXATA → OK")

# ------------------------------------------------------------
# 3. SEQUÊNCIA NUNCA VISTA
# ------------------------------------------------------------

generalized_score = learning.score(
    ["A", "X"],
    "C",
)

print()
print("Score sequência nova [A,X] -> C:", generalized_score)

assert generalized_score == 0.5

print("GENERALIZAÇÃO PARA SEQUÊNCIA NOVA → OK")

# ------------------------------------------------------------
# 4. SEQUÊNCIA SEM RELAÇÃO
# ------------------------------------------------------------

unrelated_score = learning.score(
    ["X", "Y"],
    "C",
)

print()
print("Score sequência sem relação [X,Y] -> C:", unrelated_score)

assert unrelated_score == 0.0

print("REJEIÇÃO DE SEQUÊNCIA NÃO RELACIONADA → OK")

print()
print("=" * 70)
print("GENERALIZAÇÃO DO SEQUENCE LEARNING → OK")
print("=" * 70)
