import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.context_decision_learning import ContextDecisionLearning


CODE = """
def resolver(a, b):
    return (a + b, a - b)
"""

TESTS = """
TEST: resolver(10, 3) == (7, 13)
"""


def make_search(graph):
    mutator = AutomaticASTMutator()

    def evaluator(code):
        return evaluate_problem(
            code,
            TESTS,
        ).as_dict()

    return PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=True,
        use_structure=True,
        use_graph_guidance=True,
        use_context_guidance=True,
        use_failure_guidance=True,
        use_decision_score=True,
    )


def decision_nodes(graph):
    return [
        node
        for node in graph.nodes.values()
        if node.get("type") == "decision"
    ]


def successful_decisions(graph):
    return [
        node
        for node in decision_nodes(graph)
        if node.get("data", {}).get("outcome") == "success"
    ]


def failed_decisions(graph):
    return [
        node
        for node in decision_nodes(graph)
        if node.get("data", {}).get("outcome") == "failure"
    ]


def main():
    print("=" * 70)
    print(" MORPH-GRAPH — CICLO REAL DE APRENDIZADO")
    print("=" * 70)

    graph = Graph()

    graph.add_node(
        "program",
        "code",
        {
            "code": CODE,
            "language": "python",
        },
    )

    # ---------------------------------------------------------
    # 1. PRIMEIRA EXECUÇÃO
    # ---------------------------------------------------------

    print()
    print("=== 1. PRIMEIRA EXECUÇÃO ===")

    first_search = make_search(graph)
    first_result = first_search.search("program")

    first_decisions = decision_nodes(graph)
    first_successes = successful_decisions(graph)
    first_failures = failed_decisions(graph)

    print("Sucesso:", first_result["success"])
    print("Caminho:", first_result["path"])
    print("Decisões produzidas:", len(first_decisions))
    print("Sucessos registrados:", len(first_successes))
    print("Falhas registradas:", len(first_failures))

    assert first_result["success"] is True
    assert first_decisions
    assert first_successes
    assert first_failures

    # ---------------------------------------------------------
    # 2. APRENDIZADO PRODUZIDO PELA PRÓPRIA EXECUÇÃO
    # ---------------------------------------------------------

    learner_after_first = ContextDecisionLearning(graph)

    weights_after_first = learner_after_first.learned_weights(
        CODE
    )

    print()
    print("=== 2. APRENDIZADO GERADO PELO CICLO ===")

    for key, value in weights_after_first.items():
        print(f"{key}: {value:.6f}")

    assert any(
        abs(value) > 0.0
        for value in weights_after_first.values()
    )

    # ---------------------------------------------------------
    # 2B. PROVA DO CANDIDATE LEARNING
    # ---------------------------------------------------------

    print()
    print("=== 2B. CANDIDATE LEARNING ===")

    candidate_decisions = decision_nodes(graph)

    credited = [
        node for node in candidate_decisions
        if node.get("data", {}).get("useful") is True
    ]

    print("Decisões com crédito de trajetória:", len(credited))

    for node in credited:
        data = node.get("data", {})
        scores = data.get("scores", {})

        print(
            node["id"],
            "|",
            data.get("candidate"),
            "| credit:",
            data.get("trajectory_credit"),
            "| candidate_learning:",
            scores.get("candidate_learning"),
        )

    assert credited, (
        "ERRO: nenhuma decisão recebeu crédito real da trajetória."
    )

    candidate_learning_values = [
        float(
            node.get("data", {})
                .get("scores", {})
                .get("candidate_learning", 0.0)
        )
        for node in credited
    ]

    print(
        "Maior candidate_learning entre decisões creditadas:",
        max(candidate_learning_values),
    )

    # ---------------------------------------------------------
    # 3. SEGUNDA EXECUÇÃO NO MESMO GRAFO
    # ---------------------------------------------------------

    print()
    print("=== 3. SEGUNDA EXECUÇÃO — HISTÓRICO REUTILIZADO ===")

    decisions_before_second = len(
        decision_nodes(graph)
    )

    second_search = make_search(graph)
    second_result = second_search.search("program")

    decisions_after_second = len(
        decision_nodes(graph)
    )

    second_decisions = decisions_after_second - decisions_before_second

    print("Sucesso:", second_result["success"])
    print("Caminho:", second_result["path"])
    print("Novas decisões:", second_decisions)

    assert second_result["success"] is True
    assert second_decisions > 0
    assert decisions_after_second > decisions_before_second

    # ---------------------------------------------------------
    # 4. APRENDIZADO APÓS A SEGUNDA EXECUÇÃO
    # ---------------------------------------------------------

    learner_after_second = ContextDecisionLearning(graph)

    weights_after_second = learner_after_second.learned_weights(
        CODE
    )

    print()
    print("=== 4. APRENDIZADO APÓS NOVA EXPERIÊNCIA ===")

    for key, value in weights_after_second.items():
        print(f"{key}: {value:.6f}")

    # ---------------------------------------------------------
    # 5. PROVA DE PERSISTÊNCIA DO APRENDIZADO
    # ---------------------------------------------------------

    all_decisions = decision_nodes(graph)
    all_successes = successful_decisions(graph)
    all_failures = failed_decisions(graph)

    decisions_with_context = [
        node
        for node in all_decisions
        if node.get("data", {}).get("source_code")
    ]

    print()
    print("=== 5. ESTADO FINAL DO GRAFO ===")
    print("Total de decisões:", len(all_decisions))
    print("Total de sucessos:", len(all_successes))
    print("Total de falhas:", len(all_failures))
    print(
        "Decisões com source_code:",
        len(decisions_with_context),
    )

    assert len(all_decisions) >= (
        len(first_decisions) + second_decisions
    )

    assert all_successes
    assert all_failures
    assert decisions_with_context

    # ---------------------------------------------------------
    # 6. VERIFICAÇÃO: O SEGUNDO CICLO CONSULTA O HISTÓRICO
    # ---------------------------------------------------------

    second_history_scores = [
        item["scores"]["total"]
        for item in second_search.decision_history
    ]

    second_candidate_learning_scores = [
        item["scores"].get("candidate_learning", 0.0)
        for item in second_search.decision_history
    ]

    print()
    print("=== CANDIDATE LEARNING — SEGUNDA EXECUÇÃO ===")
    print(
        "Scores candidate_learning:",
        second_candidate_learning_scores,
    )

    if second_candidate_learning_scores:
        print(
            "Maior candidate_learning:",
            max(second_candidate_learning_scores),
        )
        print(
            "Menor candidate_learning:",
            min(second_candidate_learning_scores),
        )


    print()
    assert max(second_candidate_learning_scores) > 0.0, (
        "ERRO: CandidateLearning não reutilizou "
        "nenhuma evidência positiva na segunda execução."
    )

    print("REUTILIZACAO DO CANDIDATE LEARNING → OK")

    second_sequence_learning_scores = [
        item["scores"].get("sequence_learning", 0.0)
        for item in second_search.decision_history
    ]

    print()
    print("=== SEQUENCE LEARNING — SEGUNDA EXECUÇÃO ===")
    print(
        "Scores sequence_learning:",
        second_sequence_learning_scores,
    )

    if second_sequence_learning_scores:
        print(
            "Maior sequence_learning:",
            max(second_sequence_learning_scores),
        )
        print(
            "Menor sequence_learning:",
            min(second_sequence_learning_scores),
        )

    assert second_sequence_learning_scores, (
        "ERRO: nenhuma decisão foi registrada na segunda execução."
    )

    assert max(second_sequence_learning_scores) > 0.0, (
        "ERRO: SequenceLearning não reutilizou "
        "nenhuma evidência positiva na segunda execução."
    )

    print("REUTILIZACAO DO SEQUENCE LEARNING → OK")

    print("=== 6. SCORES DA SEGUNDA EXECUÇÃO ===")

    print(
        "Quantidade de decisões:",
        len(second_history_scores),
    )

    if second_history_scores:
        print(
            "Primeiro score:",
            second_history_scores[0],
        )
        print(
            "Maior score:",
            max(second_history_scores),
        )
        print(
            "Menor score:",
            min(second_history_scores),
        )

    # O histórico não pode deixar todas as decisões
    # exatamente neutras depois de uma experiência real.
    assert any(
        abs(score) > 0.0
        for score in second_history_scores
    )

    print()
    print("PRIMEIRA EXECUÇÃO → OK")
    print("EVIDÊNCIAS REAIS → OK")
    print("APRENDIZADO GERADO PELO GRAFO → OK")
    print("HISTÓRICO REUTILIZADO → OK")
    print("SEGUNDA EXECUÇÃO → OK")
    print("CICLO REAL → OK")


if __name__ == "__main__":
    main()
