import json
import hashlib
from datetime import datetime, timezone


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.history = []

    def add_node(self, node_id, node_type, data=None):
        if node_id in self.nodes:
            raise ValueError(f"Nó já existe: {node_id}")

        node = {
            "id": node_id,
            "type": node_type,
            "data": data or {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.nodes[node_id] = node

        self.history.append({
            "action": "add_node",
            "node_id": node_id,
            "node_type": node_type,
            "timestamp": node["created_at"]
        })

        return node

    def connect(self, source, target, relation):
        if source not in self.nodes:
            raise ValueError(f"Nó de origem não existe: {source}")

        if target not in self.nodes:
            raise ValueError(f"Nó de destino não existe: {target}")

        edge = {
            "source": source,
            "target": target,
            "relation": relation
        }

        self.edges.append(edge)

        self.history.append({
            "action": "connect",
            "source": source,
            "target": target,
            "relation": relation,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        return edge

    def snapshot(self):
        graph = {
            "nodes": self.nodes,
            "edges": self.edges,
            "history": self.history
        }

        raw = json.dumps(
            graph,
            sort_keys=True,
            separators=(",", ":")
        ).encode()

        graph["hash"] = hashlib.sha256(raw).hexdigest()

        return graph

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                self.snapshot(),
                f,
                indent=2,
                ensure_ascii=False
            )
