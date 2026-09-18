import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from engine.memory import code_signature


code_a = """def resolver(a, b):
    return (a - b, a + b)
"""

code_b = """def resolver(x, y):
    return (x - y, x + y)
"""

code_c = """def calcular(valor1, valor2):
    resultado = valor1 - valor2
    return resultado
"""


sig_a = code_signature(code_a)
sig_b = code_signature(code_b)
sig_c = code_signature(code_c)

print("ASSINATURA A:", sig_a)
print("ASSINATURA B:", sig_b)
print("ASSINATURA C:", sig_c)

print()
print("A == B:", sig_a == sig_b)
print("A == C:", sig_a == sig_c)

if sig_a != sig_b:
    raise RuntimeError(
        "Falha: programas estruturalmente equivalentes "
        "não possuem a mesma assinatura."
    )

if sig_a == sig_c:
    raise RuntimeError(
        "Falha: programas estruturalmente diferentes "
        "possuem a mesma assinatura."
    )

print()
print("MEMORY GENERALIZATION: OK")
