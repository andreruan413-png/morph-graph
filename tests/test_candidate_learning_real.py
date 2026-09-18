from engine.candidate_learning import CandidateLearning
from engine.decision import DecisionScore
from engine.decision_recorder import DecisionRecorder
from engine.auto_mutation import AutomaticASTMutator
from graph.core import Graph


CODE = """
def calcular(a, b):
    return (a + b, a - b)
"""


def make_decision(
    graph,
    recorder,
    candidate,
    useful,
    source_code,
):
    score = DecisionScore.from_values(
        context=0.0,
        trajectory=0.0,
        graph=0.0,
        failure=0.0,
        transition=0.0,
        learned=0.0,
    )

    node = recorder.record(
        problem_id=None,
        candidate=candidate,
        decision_score=score,
        path=[],
        selected=useful,
        candidate_node_id=None,
        outcome="success" if useful else "failure",
        source_code=source_code,
    )

    node["data"]["useful"] = useful

    return node


def main():
    graph = Graph()
    recorder = DecisionRecorder(graph)
    mutator = AutomaticASTMutator()

    graph.add_node(
        "problem",
        "problem",
        {
            "description": "resolver soma e diferença",
        },
    )

    candidates = mutator.generate(CODE)

    target = None
    other = None

    for candidate in candidates:
        if candidate.name == "binop_0_add_to_sub":
            target = candidate

        if candidate.name == "binop_0_add_to_mult":
            other = candidate

    if target is None:
        raise AssertionError(
            "Candidato esperado não foi encontrado."
        )

    if other is None:
        raise AssertionError(
            "Segundo candidato esperado não foi encontrado."
        )

    learner = CandidateLearning(graph)

    before_target = learner.score_candidate(
        CODE,
        target,
    )

    before_other = learner.score_candidate(
        CODE,
        other,
    )

    print("=== ANTES DO APRENDIZADO ===")
    print(
        "Alvo:",
        target.name,
        before_target,
    )
    print(
        "Outro:",
        other.name,
        before_other,
    )

    # Simula decisões produzidas pelo ciclo real:
    #
    # O candidato correto recebe crédito positivo.
    # O candidato incorreto recebe crédito negativo.
    #
    # Não estamos inventando um novo algoritmo de solução;
    # estamos testando a camada que interpreta decisões reais.

    make_decision(
        graph,
        recorder,
        target,
        True,
        CODE,
    )

    make_decision(
        graph,
        recorder,
        other,
        False,
        CODE,
    )

    after_target = learner.score_candidate(
        CODE,
        target,
    )

    after_other = learner.score_candidate(
        CODE,
        other,
    )

    print()
    print("=== DEPOIS DO APRENDIZADO ===")
    print(
        "Alvo:",
        target.name,
        after_target,
    )
    print(
        "Outro:",
        other.name,
        after_other,
    )

    ranked = learner.rank(
        CODE,
        [target, other],
    )

    print()
    print("=== RANKING APRENDIDO ===")

    for item in ranked:
        print(
            item["name"],
            "| score:",
            item["candidate_learning_score"],
        )

    assert after_target > before_target
    assert after_other < before_other
    assert ranked[0]["name"] == target.name

    print()
    print("CANDIDATE LEARNING → OK")
    print("CRÉDITO POSITIVO → OK")
    print("CRÉDITO NEGATIVO → OK")
    print("PRIORIZAÇÃO → OK")


if __name__ == "__main__":
    main()
