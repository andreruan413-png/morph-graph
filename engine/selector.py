def applicable_rules(graph, rules):
    matches = []

    executed = {
        (
            item.get("source"),
            item.get("rule")
        )
        for item in graph.history
        if item.get("action") == "transform"
    }

    for node_id, node in graph.nodes.items():
        for rule in rules:

            if not rule.applies_to(node):
                continue

            if (node_id, rule.name) in executed:
                continue

            matches.append({
                "node_id": node_id,
                "rule": rule.name,
                "source_type": rule.source_type,
                "target_type": rule.target_type
            })

    return matches
