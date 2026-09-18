from graph.core import Graph
from engine.code_node import add_code_node
from engine.auto_mutation import AutomaticASTMutator
from engine.problem_evaluator import evaluate_problem
from engine.path_search import PathSearch
from engine.experience import ExperienceRecorder


SOURCE = """def resolver(a, b):
    return (a + b, a - b)
"""

TRAIN_TESTS = """TEST: resolver(10, 3) == (7, 13)
TEST: resolver(20, 5) == (15, 25)
"""

NEW_TESTS = """TEST: resolver(8, 2) == (6, 10)
TEST: resolver(30, 4) == (26, 34)
"""


def evaluator(code, tests):
    return evaluate_problem(code, tests).as_dict()


graph = Graph()

graph.add_node(
    "problem_train",
    "problem",
    {
        "description": "problema de treinamento",
        "language": "python",
    },
)

add_code_node(
    graph,
    "source",
    SOURCE,
    {"role": "source"},
)

graph.connect(
    "problem_train",
    "source",
    "has_candidate",
)

# Primeiro: cria uma experiência real de sucesso.
mutator = AutomaticASTMutator()

search_train = PathSearch(
    graph=graph,
    mutator=mutator,
    evaluator=lambda code: evaluator(code, TRAIN_TESTS),
    max_depth=3,
    beam_width=3,
    use_trajectory=False,
    use_structure=False,
    use_pruner=False,
)

result_train = search_train.search("source")

print("=== TREINAMENTO ===")
print("Sucesso:", result_train["success"])
print("Caminho:", result_train["path"])

if not result_train["success"]:
    raise SystemExit("TREINAMENTO FALHOU")

# Registra a experiência no próprio grafo.
recorder = ExperienceRecorder(graph)
experience_id = recorder.record_solution(
    "problem_train",
    result_train,
)

print("Experiência:", experience_id)

# Agora a busca nova usa ContextGuidance.
search_context = PathSearch(
    graph=graph,
    mutator=mutator,
    evaluator=lambda code: evaluator(code, NEW_TESTS),
    max_depth=3,
    beam_width=3,
    use_trajectory=False,
    use_structure=False,
    use_pruner=False,
    use_context_guidance=True,
)

# Mostra a ordem calculada antes da busca.
current_code = graph.nodes["source"]["data"]["code"]

# _candidate_sort_key usa o código atual da busca.
# Como estamos inspecionando a ordenação antes do search(),
# inicializamos esse estado explicitamente.
search_context._current_code = current_code

candidates = mutator.generate(current_code)

ranked = sorted(
    candidates,
    key=lambda candidate:
        search_context._candidate_sort_key([], candidate),
    reverse=True,
)

print()
print("=== CONTEXT GUIDANCE ===")

for candidate in ranked[:5]:
    score = search_context.context_guidance.candidate_score(
        current_code,
        candidate,
        [],
    )
    print(
        candidate.name,
        "| context_score:",
        score,
        "| região:",
        candidate.region_index,
    )

result_context = search_context.search("source")

print()
print("=== RESULTADO ===")
print("Sucesso:", result_context["success"])
print("Caminho:", result_context["path"])

if not result_context["success"]:
    raise SystemExit("BUSCA COM CONTEXTO FALHOU")

print()
print("CONTEXT GUIDANCE → EXECUTADO: OK")
print("EXPERIÊNCIA → PRIORIDADE: OK")
print("PATHSEARCH → CONTEXT GUIDANCE: OK")
