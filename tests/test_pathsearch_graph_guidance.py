from graph.core import Graph
from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch


SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""

TESTS = """TEST: resolver(10, 3) == (7, 13)
TEST: resolver(20, 5) == (15, 25)
"""


def executar(graph, use_graph_guidance):
    mutator = AutomaticASTMutator()

    def evaluator(code):
        return evaluate_problem(code, TESTS).as_dict()

    search = PathSearch(
        graph=graph,
        mutator=mutator,
        evaluator=evaluator,
        max_depth=3,
        beam_width=3,
        use_trajectory=False,
        use_structure=False,
        use_pruner=False,
        use_graph_guidance=use_graph_guidance,
    )

    return search.search("source")


def adicionar_experiencia(graph):
    graph.add_node(
        "experience_1",
        "experience",
        {
            "score": 1.0,
            "trajectory": [
                {
                    "rule": "binop_1_sub_to_add",
                    "region_index": 1,
                    "region_type": "BinOp",
                },
                {
                    "rule": "binop_0_add_to_sub",
                    "region_index": 0,
                    "region_type": "BinOp",
                },
            ],
        },
    )


graph = Graph()

add_code_node(
    graph,
    "source",
    SOURCE,
    {"role": "source"},
)


print("\n=== BUSCA SEM EXPERIÊNCIA ===")

resultado_sem = executar(
    graph,
    use_graph_guidance=True,
)

print("Sucesso:", resultado_sem["success"])
print("Caminho:", resultado_sem["path"])

avaliacoes_sem = resultado_sem["evaluated_candidates"]

print("\nPrimeiros candidatos avaliados:")

for item in avaliacoes_sem[:5]:
    print(
        item["candidate"],
        "| score:",
        item["score"],
        "| região:",
        item["region_index"],
    )


adicionar_experiencia(graph)


print("\n=== BUSCA COM EXPERIÊNCIA NO GRAFO ===")

resultado_com = executar(
    graph,
    use_graph_guidance=True,
)

print("Sucesso:", resultado_com["success"])
print("Caminho:", resultado_com["path"])

avaliacoes_com = resultado_com["evaluated_candidates"]

print("\nPrimeiros candidatos avaliados:")

for item in avaliacoes_com[:5]:
    print(
        item["candidate"],
        "| score:",
        item["score"],
        "| região:",
        item["region_index"],
    )


primeiro_sem = (
    avaliacoes_sem[0]["candidate"]
    if avaliacoes_sem
    else None
)

primeiro_com = (
    avaliacoes_com[0]["candidate"]
    if avaliacoes_com
    else None
)


print("\n=== RESULTADO ===")
print("Primeiro sem experiência:", primeiro_sem)
print("Primeiro com experiência:", primeiro_com)

if primeiro_sem != primeiro_com:
    print("GRAPH GUIDANCE → MUDOU A DECISÃO: OK")
else:
    print("GRAPH GUIDANCE → NÃO MUDOU A PRIMEIRA DECISÃO")

if resultado_com["success"]:
    print("PATHSEARCH COM GRAPH GUIDANCE: OK")
else:
    print("PATHSEARCH COM GRAPH GUIDANCE: FALHOU")
