from engine.code_node import add_code_node


class CodeMutationRule:
    def __init__(self, name, old_text, new_text):
        self.name = name
        self.old_text = old_text
        self.new_text = new_text

    def applies_to(self, node):
        if node["type"] != "code":
            return False

        return self.old_text in node["data"].get("code", "")

    def transform(self, graph, source_id, new_id):
        source = graph.nodes[source_id]

        if not self.applies_to(source):
            raise ValueError(
                f"A regra '{self.name}' não pode ser aplicada."
            )

        old_code = source["data"]["code"]

        new_code = old_code.replace(
            self.old_text,
            self.new_text,
            1
        )

        node = add_code_node(
            graph,
            new_id,
            new_code,
            {
                "generated_by": self.name,
                "source_node": source_id,
                "mutation": {
                    "old": self.old_text,
                    "new": self.new_text
                }
            }
        )

        graph.connect(
            source_id,
            new_id,
            self.name
        )

        graph.history.append({
            "action": "transform",
            "source": source_id,
            "rule": self.name,
            "target": new_id
        })

        return node
