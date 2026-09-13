def rule_statistics(graph):
    stats = {}

    for node in graph.nodes.values():
        if node["type"] != "evaluation":
            continue

        data = node["data"]

        target_id = data.get("target_node")
        score = float(data.get("score", 0.0))

        target = graph.nodes.get(target_id)

        if not target:
            continue

        rule = target["data"].get("generated_by")

        if not rule:
            continue

        if rule not in stats:
            stats[rule] = {
                "attempts": 0,
                "successes": 0,
                "total_score": 0.0
            }

        stats[rule]["attempts"] += 1
        stats[rule]["total_score"] += score

        if data.get("success"):
            stats[rule]["successes"] += 1

    for rule, data in stats.items():
        data["average_score"] = (
            data["total_score"] / data["attempts"]
        )

    return stats


def rank_rules(graph, rules):
    stats = rule_statistics(graph)

    ranked = []

    for rule in rules:
        data = stats.get(
            rule.name,
            {
                "attempts": 0,
                "successes": 0,
                "total_score": 0.0,
                "average_score": 0.0
            }
        )

        ranked.append({
            "rule": rule.name,
            "attempts": data["attempts"],
            "successes": data["successes"],
            "average_score": data["average_score"]
        })

    ranked.sort(
        key=lambda item: (
            item["average_score"],
            item["successes"]
        ),
        reverse=True
    )

    return ranked
