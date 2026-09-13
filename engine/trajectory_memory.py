class TrajectoryMemory:

    def __init__(self, graph):
        self.graph = graph

    def _experiences(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node["type"] == "experience"
        ]

    def successful_trajectories(self):
        trajectories = []

        for experience in self._experiences():

            data = experience["data"]

            score = float(
                data.get("score", 0.0)
            )

            if score < 1.0:
                continue

            generations = data.get(
                "generations",
                []
            )

            path = []

            for generation in generations:

                selected = generation.get(
                    "selected",
                    {}
                )

                rule = selected.get(
                    "rule"
                )

                if rule:
                    path.append(rule)

            if not path:
                continue

            trajectories.append({
                "experience_id": experience["id"],
                "problem_id": data.get(
                    "problem_id"
                ),
                "solution_node": data.get(
                    "solution_node"
                ),
                "score": score,
                "path": path
            })

        return trajectories

    def paths_for_rule(self, rule_name):

        matches = []

        for trajectory in (
            self.successful_trajectories()
        ):

            if rule_name in trajectory["path"]:

                matches.append(
                    trajectory
                )

        return matches

    def next_steps(self, prefix):

        suggestions = {}

        prefix = list(prefix)

        for trajectory in (
            self.successful_trajectories()
        ):

            path = trajectory["path"]

            if len(path) <= len(prefix):
                continue

            if path[:len(prefix)] != prefix:
                continue

            next_rule = path[len(prefix)]

            suggestions[next_rule] = (
                suggestions.get(
                    next_rule,
                    0
                ) + 1
            )

        return dict(
            sorted(
                suggestions.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

    def best_path(self):

        trajectories = (
            self.successful_trajectories()
        )

        if not trajectories:
            return None

        return max(
            trajectories,
            key=lambda item: (
                item["score"],
                len(item["path"])
            )
        )
