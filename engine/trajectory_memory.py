class TrajectoryMemory:
    def __init__(self, graph, problem_id=None):
        self.graph = graph
        self.problem_id = problem_id

    def _experiences(self):
        return [
            node
            for node in self.graph.nodes.values()
            if node["type"] == "experience"
        ]

    def _extract_path(self, experience):
        path = []

        for generation in experience["data"].get(
            "generations",
            []
        ):
            selected = generation.get(
                "selected",
                {}
            )

            rule = selected.get("rule")

            if not rule:
                continue

            path.append({
                "rule": rule,
                "region_index": selected.get(
                    "region_index"
                ),
                "region_type": selected.get(
                    "region_type"
                ),
            })

        return path

    def successful_trajectories(self):
        trajectories = []

        for experience in self._experiences():
            data = experience["data"]

            if (
                self.problem_id is not None
                and data.get("problem_id") != self.problem_id
            ):
                continue

            score = float(
                data.get("score", 0.0)
            )

            if score < 1.0:
                continue

            path = self._extract_path(
                experience
            )

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
                "path": path,
            })

        return trajectories

    def paths_for_rule(self, rule_name):
        return [
            trajectory
            for trajectory in self.successful_trajectories()
            if any(
                step["rule"] == rule_name
                for step in trajectory["path"]
            )
        ]

    def next_steps(self, prefix):
        suggestions = {}

        prefix = list(prefix)

        for trajectory in self.successful_trajectories():
            path = trajectory["path"]

            path_rules = [
                step["rule"]
                for step in path
            ]

            if len(path_rules) <= len(prefix):
                continue

            if path_rules[:len(prefix)] != prefix:
                continue

            next_step = path[len(prefix)]
            next_rule = next_step["rule"]

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
                reverse=True,
            )
        )

    def next_regions(self, prefix):
        suggestions = {}

        prefix = list(prefix)

        for trajectory in self.successful_trajectories():
            path = trajectory["path"]

            path_rules = [
                step["rule"]
                for step in path
            ]

            if len(path_rules) <= len(prefix):
                continue

            if path_rules[:len(prefix)] != prefix:
                continue

            step = path[len(prefix)]

            key = (
                step["rule"],
                step["region_index"],
                step["region_type"],
            )

            suggestions[key] = (
                suggestions.get(key, 0)
                + 1
            )

        return dict(
            sorted(
                suggestions.items(),
                key=lambda item: item[1],
                reverse=True,
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
                -len(item["path"]),
            ),
        )
