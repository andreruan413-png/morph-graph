def add_code_node(graph, node_id, code, metadata=None):
    data = {
        "code": code,
        "language": "python"
    }

    if metadata:
        data.update(metadata)

    return graph.add_node(
        node_id,
        "code",
        data
    )
