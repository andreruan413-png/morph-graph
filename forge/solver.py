from engine.evolution import EvolutionEngine
from forge.ai_agent import AIRepairAgent


class ForgeSolver:
    def __init__(self, graph, tests, ai_agent=None):
        self.graph = graph
        self.tests = tests
        self.ai_agent = ai_agent or AIRepairAgent()

    def solve(self, problem_id, generations=10):
        engine = EvolutionEngine(
            self.graph,
            tests=self.tests,
        )

        return engine.evolve(
            problem_id,
            generations=generations,
        )

    def analyze_with_ai(self, source, error=""):
        return self.ai_agent.analyze(
            source=source,
            error=error,
            tests=self.tests,
        )
