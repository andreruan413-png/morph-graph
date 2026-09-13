from engine.selector import applicable_rules
from engine.learning import rank_rules


class MorphRunner:
    def __init__(self, graph, rules):
        self.graph = graph
        self.rules = rules

    def find_moves(self):
        return applicable_rules(self.graph, self.rules)

    def _next_node_id(self):
        index = 1

        while f"node_{index:03d}" in self.graph.nodes:
            index += 1

        return f"node_{index:03d}"

    def choose_move(self):
        moves = self.find_moves()

        if not moves:
            return None

        ranking = rank_rules(
            self.graph,
            self.rules
        )

        ranking_position = {
            item["rule"]: index
            for index, item in enumerate(ranking)
        }

        moves.sort(
            key=lambda move: ranking_position.get(
                move["rule"],
                len(ranking)
            )
        )

        return moves[0]

    def step(self):
        move = self.choose_move()

        if not move:
            return None

        new_id = self._next_node_id()

        rule = next(
            rule for rule in self.rules
            if rule.name == move["rule"]
        )

        rule.transform(
            self.graph,
            move["node_id"],
            new_id,
            {
                "generated_by": rule.name,
                "source_node": move["node_id"]
            }
        )

        self.graph.history.append({
            "action": "transform",
            "source": move["node_id"],
            "rule": rule.name,
            "target": new_id
        })

        return {
            "source": move["node_id"],
            "rule": move["rule"],
            "created": new_id
        }
