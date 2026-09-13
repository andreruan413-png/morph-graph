class Evaluation:
    def __init__(self, success, score, reason=""):
        self.success = success
        self.score = float(score)
        self.reason = reason

    def as_dict(self):
        return {
            "success": self.success,
            "score": self.score,
            "reason": self.reason
        }


def evaluate_node(node, expected_type):
    if node["type"] == expected_type:
        return Evaluation(
            success=True,
            score=1.0,
            reason="tipo produzido conforme esperado"
        )

    return Evaluation(
        success=False,
        score=0.0,
        reason="tipo produzido diferente do esperado"
    )


def record_evaluation(graph, node_id, evaluation):
    evaluation_id = f"evaluation_{len(graph.history):03d}"

    graph.add_node(
        evaluation_id,
        "evaluation",
        {
            "target_node": node_id,
            **evaluation.as_dict()
        }
    )

    graph.connect(
        node_id,
        evaluation_id,
        "evaluated_by"
    )

    return evaluation_id
