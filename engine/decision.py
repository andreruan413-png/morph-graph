class DecisionScore:
    """
    Consolida as evidências disponíveis para um candidato.

    O score não substitui as memórias existentes.
    Ele cria uma camada única para representar a decisão.
    """

    def __init__(
        self,
        context=0.0,
        trajectory=0.0,
        graph=0.0,
        failure=0.0,
        transition=0.0,
        learned=0.0,
        candidate_learning=0.0,
        sequence_learning=0.0,
        structural_sequence=0.0,
        fitness_delta=0.0,
    ):
        self.context = float(context)
        self.trajectory = float(trajectory)
        self.graph = float(graph)
        self.failure = float(failure)
        self.transition = float(transition)
        self.learned = float(learned)
        self.candidate_learning = float(candidate_learning)
        self.sequence_learning = float(sequence_learning)
        self.structural_sequence = float(structural_sequence)
        self.fitness_delta = float(fitness_delta)

    @property
    def total(self):
        return (
            self.context
            + self.trajectory
            + self.graph
            + self.failure
            + self.transition
            + self.learned
            + self.candidate_learning
            + self.sequence_learning
            + self.structural_sequence + self.fitness_delta
        )

    def as_dict(self):
        return {
            "context": self.context,
            "trajectory": self.trajectory,
            "graph": self.graph,
            "failure": self.failure,
            "transition": self.transition,
            "learned": self.learned,
            "candidate_learning": self.candidate_learning,
            "sequence_learning": self.sequence_learning,
            "structural_sequence": self.structural_sequence,
            "fitness_delta": self.fitness_delta,
            "total": self.total,
        }

    @classmethod
    def from_values(
        cls,
        context=0.0,
        trajectory=0.0,
        graph=0.0,
        failure=0.0,
        transition=0.0,
        learned=0.0,
        candidate_learning=0.0,
        sequence_learning=0.0,
        structural_sequence=0.0,
        fitness_delta=0.0,
    ):
        return cls(
            context=context,
            trajectory=trajectory,
            graph=graph,
            failure=failure,
            transition=transition,
            learned=learned,
            candidate_learning=candidate_learning,
            sequence_learning=sequence_learning,
            structural_sequence=structural_sequence,
            fitness_delta=fitness_delta,
        )
