from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.failure_guidance import FailureGuidance


def make_candidate(source, candidate_name):
    mutator = AutomaticASTMutator()

    candidates = mutator.generate(source)

    for candidate in candidates:
        if candidate.name == candidate_name:
            return candidate

    raise AssertionError(
        f"Candidato não encontrado: {candidate_name}"
    )


graph = Graph()

# =========================================================
# CONTEXTO A
# =========================================================

code_a = """def resolver(a, b):
    return a + b
"""

graph.add_node(
    "source_a",
    "code",
    {
        "code": code_a,
        "language": "python",
    },
)

candidate_a = make_candidate(
    code_a,
    "binop_0_add_to_mult",
)

graph.add_node(
    "failed_a",
    "code",
    {
        "code": candidate_a.code(),
        "language": "python",
        "generated_by": candidate_a.name,
        "source_node": "source_a",
        "region_index": candidate_a.region_index,
        "region_type": candidate_a.region_type,
    },
)

graph.connect(
    "source_a",
    "failed_a",
    candidate_a.name,
)

graph.add_node(
    "evaluation_a",
    "evaluation",
    {
        "target_node": "failed_a",
        "success": False,
        "score": 0.0,
        "reason": "testes falharam",
    },
)

graph.connect(
    "failed_a",
    "evaluation_a",
    "evaluated_by",
)

guidance = FailureGuidance(graph)

# =========================================================
# MESMO CONTEXTO
# =========================================================

same_context_score = guidance.score_candidate(
    candidate_a,
    current_code=code_a,
    similarity_threshold=0.5,
)

print("=== MESMO CONTEXTO ===")
print(
    "Transformação:",
    candidate_a.name,
)
print(
    "Score:",
    same_context_score,
)

if same_context_score >= 0:
    raise AssertionError(
        "Falha histórica semelhante não foi penalizada."
    )

print(
    "FALHA CONTEXTUAL → PENALIZA: OK"
)

# =========================================================
# CONTEXTO DIFERENTE
#
# Ainda existe uma soma, portanto o mesmo tipo de
# transformação continua disponível.
#
# Mas a estrutura agora possui condição, comparação
# e outro caminho de execução.
# =========================================================

different_code = """def resolver(a, b):
    if a > 0:
        resultado = a + b
        return resultado

    return a + b
"""

different_candidate = make_candidate(
    different_code,
    "binop_0_add_to_mult",
)

different_context_score = guidance.score_candidate(
    different_candidate,
    current_code=different_code,
    similarity_threshold=0.95,
)

print()
print("=== CONTEXTO DIFERENTE ===")
print(
    "Transformação:",
    different_candidate.name,
)
print(
    "Score:",
    different_context_score,
)

if different_context_score != 0.0:
    raise AssertionError(
        "Falha de contexto diferente influenciou indevidamente."
    )

print(
    "CONTEXTO DIFERENTE → NÃO PENALIZA: OK"
)

# =========================================================
# INSPEÇÃO
# =========================================================

contextual = guidance.contextual_failures(
    code_a,
    similarity_threshold=0.5,
)

print()
print("=== MEMÓRIA CONTEXTUAL ===")

for item in contextual:
    print(
        item["rule"],
        "| similaridade:",
        round(
            item["similarity"],
            6,
        ),
        "| região:",
        item["region_index"],
        "| tipo:",
        item["region_type"],
    )

if not contextual:
    raise AssertionError(
        "Falha contextual não foi recuperada."
    )

print()
print("FAILURE CONTEXT GUIDANCE → OK")
print("MEMÓRIA NEGATIVA → CONTEXTO: OK")
