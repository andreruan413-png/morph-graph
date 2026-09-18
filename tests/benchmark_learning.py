import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from graph.core import Graph
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.trajectory_guidance import TrajectoryGuidance


def evaluator_factory(tests):
    def evaluator(code):
        return evaluate_problem(
            code,
            tests
        ).as_dict()

    return evaluator


def create_problem(graph, problem_id):
    code = """
def calcular(a, b):
    return (a - b, a + b)
"""

    tests = """
TEST: assert calcular(2, 3)[0] == 5
TEST: assert calcular(2, 3)[1] == 6
"""

    graph.add_node(
        problem_id,
        "code",
        {
            "code": code,
            "language": "python"
        }
    )

    return tests


def add_learning_experience(graph):
    graph.add_node(
        "learned_solution",
        "code",
        {
            "code": """
def calcular(a, b):
    return (a + b, a * b)
"""
        }
    )

    graph.add_node(
        "experience_seed",
        "experience",
        {
            "problem_id": "historical_problem",
            "solution_node": "learned_solution",
            "score": 1.0,
            "generations": [
                {
                    "selected": {
                        "rule": "binop_0_sub_to_add"
                    }
                },
                {
                    "selected": {
                        "rule": "binop_1_add_to_mult"
                    }
                }
            ]
        }
    )


def run_search(
    graph,
    problem_id,
    tests,
    learned
):
    mutator = AutomaticASTMutator()

    evaluator = evaluator_factory(tests)

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3
    )

    if not learned:
        search.trajectory_guidance = None

        class NoGuidance:

            def priorities(self, path):
                return {}

        search.trajectory_guidance = NoGuidance()

    return search.search(problem_id)


def main():

    repetitions = 20

    baseline = []
    learned = []

    print()
    print("=" * 60)
    print("       MORPH-GRAPH — EXPERIMENTO DE APRENDIZAGEM")
    print("=" * 60)

    for i in range(1, repetitions + 1):

        graph_base = Graph()

        tests_base = create_problem(
            graph_base,
            f"program_base_{i:03d}"
        )

        result_base = run_search(
            graph_base,
            f"program_base_{i:03d}",
            tests_base,
            learned=False
        )

        baseline.append(result_base)

        graph_learned = Graph()

        tests_learned = create_problem(
            graph_learned,
            f"program_learned_{i:03d}"
        )

        add_learning_experience(
            graph_learned
        )

        result_learned = run_search(
            graph_learned,
            f"program_learned_{i:03d}",
            tests_learned,
            learned=True
        )

        learned.append(result_learned)

        print(
            f"\nProblema {i:02d}: "
            f"baseline={result_base['explored']} "
            f"| aprendido={result_learned['explored']}"
        )

    baseline_success = sum(
        1
        for result in baseline
        if result["success"]
    )

    learned_success = sum(
        1
        for result in learned
        if result["success"]
    )

    baseline_explored = sum(
        result["explored"]
        for result in baseline
    )

    learned_explored = sum(
        result["explored"]
        for result in learned
    )

    print()
    print("=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)

    print(
        f"Problemas:              {repetitions}"
    )

    print(
        f"Baseline resolvidos:    {baseline_success}/{repetitions}"
    )

    print(
        f"Aprendido resolvidos:   {learned_success}/{repetitions}"
    )

    print(
        f"Baseline nós explorados:  {baseline_explored}"
    )

    print(
        f"Aprendido nós explorados: {learned_explored}"
    )

    if baseline_explored:
        reduction = (
            1 -
            learned_explored / baseline_explored
        ) * 100

        print(
            f"Redução da busca:       {reduction:.2f}%"
        )

    print()
    print("=" * 60)

    assert learned_success == repetitions

    print("EXPERIMENTO: OK")


if __name__ == "__main__":
    main()
