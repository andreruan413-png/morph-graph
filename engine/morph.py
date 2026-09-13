import json
from graph.core import Graph


def morph(graph, source_id, new_id, node_type, data=None):
    graph.add_node(
        new_id,
        node_type,
        data
    )

    graph.connect(
        source_id,
        new_id,
        "created"
    )

    return graph


if __name__ == "__main__":
    graph = Graph()

    graph.add_node(
        "origin",
        "seed",
        {"message": "primeiro nó"}
    )

    morph(
        graph,
        "origin",
        "node_001",
        "generated",
        {"message": "nó criado por transformação"}
    )

    graph.save("graph.json")

    print(json.dumps(graph.snapshot(), indent=2, ensure_ascii=False))
