from graph.core import Graph
from engine.decision import DecisionScore
from engine.decision_recorder import DecisionRecorder


graph = Graph()

graph.add_node(
    "problem_001",
    "problem",
    {
        "description": "teste"
    }
)

graph.add_node(
    "candidate_old",
    "code",
    {
        "code": "return a - b",
        "generated_by": "binop_0_add_to_sub",
    }
)

graph.add_node(
    "candidate_new",
    "code",
    {
        "code": "return a - b",
        "generated_by": "binop_0_add_to_sub",
    }
)

graph.connect(
    "problem_001",
    "candidate_old",
    "has_candidate",
)

graph.connect(
    "problem_001",
    "candidate_new",
    "has_candidate",
)


class Candidate:
    name = "binop_0_add_to_sub"
    region_index = 0
    region_type = "BinOp"


candidate = Candidate()

score = DecisionScore.from_values(
    context=100,
    trajectory=20,
    graph=10,
    failure=0,
    transition=5,
    learned=10,
)

recorder = DecisionRecorder(graph)

node = recorder.record(
    "problem_001",
    candidate,
    score,
    path=["binop_0_add_to_sub"],
    selected=True,
    candidate_node_id="candidate_new",
    outcome="success",
)

print("=== DECISION ===")
print(f"ID: {node['id']}")
print(f"Candidato: {node['data']['candidate']}")
print(
    f"Candidate node: "
    f"{node['data']['candidate_node_id']}"
)
print(f"Outcome: {node['data']['outcome']}")

decision_target = None

for edge in graph.edges:
    if (
        edge.get("source") == node["id"]
        and edge.get("relation") == "decision_for"
    ):
        decision_target = edge.get("target")
        break

print()
print("=== LIGAÇÃO ===")
print(f"Decision → candidate: {decision_target}")

assert decision_target == "candidate_new"

assert (
    node["data"]["candidate_node_id"]
    == "candidate_new"
)

assert node["data"]["outcome"] == "success"

print()
print("DECISION → CANDIDATO EXATO: OK")
print("OUTCOME PERSISTENTE: OK")
print("DECISION RECORDER → OK")
