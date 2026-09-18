import tempfile
from pathlib import Path

from graph.core import Graph
from engine.decision import DecisionScore
from engine.decision_recorder import DecisionRecorder


class Candidate:
    name = "binop_0_add_to_sub"
    region_index = 0
    region_type = "BinOp"


graph = Graph()

graph.add_node(
    "problem_001",
    "problem",
    {
        "description": "resolver a - b",
    },
)

candidate = Candidate()

score = DecisionScore.from_values(
    context=150.0,
    trajectory=20.0,
    graph=10.0,
    failure=0.0,
    transition=5.0,
    learned=10.0,
)

recorder = DecisionRecorder(graph)

decision = recorder.record(
    problem_id="problem_001",
    candidate=candidate,
    decision_score=score,
    path=[],
    selected=True,
)

print("=== DECISION NO GRAPH ===")
print("ID:", decision["id"])
print("Tipo:", decision["type"])
print("Candidato:", decision["data"]["candidate"])
print("Selecionado:", decision["data"]["selected"])
print("Scores:", decision["data"]["scores"])

assert decision["type"] == "decision"
assert decision["data"]["candidate"] == "binop_0_add_to_sub"
assert decision["data"]["selected"] is True
assert decision["data"]["scores"]["total"] == 195.0

assert any(
    edge["source"] == "problem_001"
    and edge["target"] == decision["id"]
    and edge["relation"] == "produced_decision"
    for edge in graph.edges
)

print("PROBLEMA → DECISION: OK")

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "decision_graph.json"

    graph.save(path)

    loaded = Graph.load(path)

    restored = loaded.nodes.get(decision["id"])

    assert restored is not None
    assert restored["type"] == "decision"
    assert restored["data"]["candidate"] == "binop_0_add_to_sub"
    assert restored["data"]["scores"]["total"] == 195.0
    assert restored["data"]["selected"] is True

    print("SAVE → LOAD: OK")
    print("DECISION PERSISTENTE: OK")

print()
print("DECISION → GRAPH → PERSISTÊNCIA: OK")
