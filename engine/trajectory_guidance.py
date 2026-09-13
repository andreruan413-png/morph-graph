from engine.trajectory_memory import TrajectoryMemory


class TrajectoryGuidance:

    def __init__(self, graph):
        self.memory = TrajectoryMemory(graph)

    def priorities(self, path):
        """
        Retorna a prioridade das próximas regras com base
        nas trajetórias que já deram certo.

        Quanto mais vezes uma regra apareceu como próximo
        passo de uma trajetória bem-sucedida, maior a prioridade.
        """
        return self.memory.next_steps(path)

    def priority(self, path, rule_name):
        priorities = self.priorities(path)
        return priorities.get(rule_name, 0)
