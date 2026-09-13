from graph.core import Graph


class Problem:

    def __init__(
        self,
        problem_id,
        description,
        tests,
        language="python"
    ):

        self.problem_id = problem_id
        self.description = description
        self.tests = tests
        self.language = language

    def add_to_graph(self, graph):

        problem_node = graph.add_node(
            self.problem_id,
            "problem",
            {
                "description": self.description,
                "language": self.language
            }
        )

        specification_id = (
            f"{self.problem_id}_spec"
        )

        tests_id = (
            f"{self.problem_id}_tests"
        )

        graph.add_node(
            specification_id,
            "specification",
            {
                "description": self.description
            }
        )

        graph.add_node(
            tests_id,
            "tests",
            {
                "content": self.tests
            }
        )

        graph.connect(
            self.problem_id,
            specification_id,
            "has_specification"
        )

        graph.connect(
            self.problem_id,
            tests_id,
            "has_tests"
        )

        return problem_node
