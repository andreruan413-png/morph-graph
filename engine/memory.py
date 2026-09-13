import ast
import hashlib


def code_signature(code):
    """
    Gera uma assinatura estrutural do código.

    A formatação e os espaços são ignorados.
    O objetivo é reconhecer quando o MORPH-GRAPH
    chegou novamente à mesma estrutura de programa.
    """

    tree = ast.parse(code)

    normalized = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


class GraphMemory:

    def __init__(self, graph):
        self.graph = graph

    def signatures(self):
        """
        Retorna as assinaturas dos códigos que já existem
        no grafo.
        """

        known = {}

        for node_id, node in self.graph.nodes.items():

            if node["type"] != "code":
                continue

            code = node["data"].get("code")

            if not code:
                continue

            try:
                signature = code_signature(code)
            except SyntaxError:
                continue

            known[signature] = node_id

        return known

    def has_seen(self, code):
        """
        Verifica se a estrutura do código já apareceu no grafo.
        """

        signature = code_signature(code)

        return signature in self.signatures()

    def remember(self, node_id):
        """
        Retorna a assinatura do nó.
        A memória é persistida no próprio grafo,
        porque o código já está registrado como nó.
        """

        node = self.graph.nodes[node_id]

        if node["type"] != "code":
            raise ValueError(
                "Somente nós do tipo 'code' podem ser memorizados."
            )

        code = node["data"].get("code")

        if not code:
            raise ValueError(
                f"Nó '{node_id}' não contém código."
            )

        signature = code_signature(code)

        node["data"]["signature"] = signature

        return signature

    def is_duplicate(self, node_id):
        """
        Verifica se o nó possui uma estrutura igual
        à de outro nó anterior.
        """

        node = self.graph.nodes[node_id]

        if node["type"] != "code":
            return False

        code = node["data"].get("code")

        if not code:
            return False

        signature = code_signature(code)

        for other_id, other in self.graph.nodes.items():

            if other_id == node_id:
                continue

            if other["type"] != "code":
                continue

            other_code = other["data"].get("code")

            if not other_code:
                continue

            try:
                other_signature = code_signature(
                    other_code
                )
            except SyntaxError:
                continue

            if signature == other_signature:
                return True

        return False
