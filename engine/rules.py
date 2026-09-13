class TransformationRule:
    def __init__(self, name, source_type, target_type):
        self.name = name
        self.source_type = source_type
        self.target_type = target_type

    def applies_to(self, node):
        return node["type"] == self.source_type

    def transform(self, graph, source_id, new_id, data=None):
        source = graph.nodes[source_id]

        if not self.applies_to(source):
            raise ValueError(
                f"A regra '{self.name}' não pode transformar "
                f"o nó do tipo '{source['type']}'"
            )

        graph.add_node(
            new_id,
            self.target_type,
            data or {}
        )

        graph.connect(
            source_id,
            new_id,
            self.name
        )

        return graph.nodes[new_id]
