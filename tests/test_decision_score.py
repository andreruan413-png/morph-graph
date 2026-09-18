from engine.decision import DecisionScore


# =========================================================
# CANDIDATO POSITIVO
# =========================================================

positive = DecisionScore(
    context=150.0,
    trajectory=20.0,
    graph=10.0,
    failure=0.0,
    transition=5.0,
    learned=10.0,
)

print("=== CANDIDATO POSITIVO ===")
print(positive.as_dict())

if positive.total != 195.0:
    raise AssertionError(
        f"Score positivo incorreto: {positive.total}"
    )

print(
    "EVIDÊNCIAS POSITIVAS → DECISION SCORE: OK"
)


# =========================================================
# CANDIDATO COM FALHA
# =========================================================

negative = DecisionScore(
    context=150.0,
    trajectory=20.0,
    graph=10.0,
    failure=-15.0,
    transition=5.0,
    learned=10.0,
)

print()
print("=== CANDIDATO COM FALHA ===")
print(negative.as_dict())

if negative.total != 180.0:
    raise AssertionError(
        f"Score negativo incorreto: {negative.total}"
    )

if negative.total >= positive.total:
    raise AssertionError(
        "Falha não reduziu a decisão."
    )

print(
    "MEMÓRIA NEGATIVA → REDUZ DECISION SCORE: OK"
)


# =========================================================
# COMPARAÇÃO
# =========================================================

unknown = DecisionScore()

print()
print("=== COMPARAÇÃO ===")
print(
    "Positivo:",
    positive.total,
)
print(
    "Com falha:",
    negative.total,
)
print(
    "Desconhecido:",
    unknown.total,
)

if positive.total <= negative.total:
    raise AssertionError(
        "Candidato positivo deveria ter maior prioridade."
    )

if negative.total <= unknown.total:
    raise AssertionError(
        "Este teste esperava evidência positiva líquida."
    )

print()
print("DECISION SCORE → OK")
print("EVIDÊNCIA POSITIVA + NEGATIVA → CONSOLIDADA: OK")
