import ast

from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem


BUGGY_CODE = """
def calculate(a, b):
    return a + b
"""

BUGGY_TESTS = """
TEST: assert calculate(10, 3) == 7
TEST: assert calculate(20, 5) == 15
TEST: assert calculate(8, 2) == 6
"""


def evaluate(code):
    return evaluate_problem(code, BUGGY_TESTS).as_dict()


def mutation_info(original, candidate):
    original_result = evaluate(original)
    candidate_result = evaluate(candidate)

    return {
        "original_score": original_result["score"],
        "candidate_score": candidate_result["score"],
        "delta": candidate_result["score"] - original_result["score"],
        "original_success": original_result["success"],
        "candidate_success": candidate_result["success"],
    }


def main():
    mutator = AutomaticASTMutator()
    candidates = mutator.generate(BUGGY_CODE)

    print("=" * 70)
    print("MORPH-GRAPH — TESTE DE MELHORIA SEMÂNTICA")
    print("=" * 70)

    print("\nCódigo original:")
    print(BUGGY_CODE.strip())

    original = evaluate(BUGGY_CODE)

    print("\nResultado original:")
    print("Score:", original["score"])
    print("Sucesso:", original["success"])

    neutral = None
    corrective = None

    for candidate in candidates:
        code = candidate.code()
        info = mutation_info(BUGGY_CODE, code)

        print("\n--- CANDIDATO ---")
        print("Nome:", candidate.name)
        print("Tipo:", getattr(candidate, "mutation_type", None))
        print("Região:", getattr(candidate, "region_index", None))
        print("Score:", info["candidate_score"])
        print("Delta:", info["delta"])
        print("Sucesso:", info["candidate_success"])

        if info["delta"] == 0 and neutral is None:
            neutral = (candidate, info)

        if info["delta"] > 0 and corrective is None:
            corrective = (candidate, info)

    print("\n" + "=" * 70)
    print("CLASSIFICAÇÃO")
    print("=" * 70)

    if neutral:
        candidate, info = neutral
        print("\nTransformação neutra encontrada:")
        print(candidate.name)
        print("Delta:", info["delta"])
    else:
        print("\nNenhuma transformação neutra encontrada.")

    if corrective:
        candidate, info = corrective
        print("\nTransformação com melhoria encontrada:")
        print(candidate.name)
        print("Delta:", info["delta"])
    else:
        print("\nNenhuma transformação com melhoria encontrada.")

    print("\n" + "=" * 70)

    if neutral and corrective:
        print("RESULTADO: DISTINÇÃO SEMÂNTICA DISPONÍVEL")
        print("O sistema consegue medir diferença entre transformação neutra e melhoria.")
    else:
        print("RESULTADO: BENCHMARK INSUFICIENTE")
        print("Não foi possível observar as duas classes de transformação.")

    print("=" * 70)


if __name__ == "__main__":
    main()
