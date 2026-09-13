from graph.core import Graph

from engine.trajectory_memory import (
    TrajectoryMemory
)


graph = Graph()


graph.add_node(
    "experience_001",
    "experience",
    {
        "problem_id": "problem_001",
        "solution_node": "code_003",
        "score": 1.0,
        "generations": [
            {
                "generation": 1,
                "source": "candidate_001",
                "selected": {
                    "node_id": "code_001",
                    "rule": "sub_to_add"
                }
            },
            {
                "generation": 2,
                "source": "code_001",
                "selected": {
                    "node_id": "code_002",
                    "rule": "swap_operands"
                }
            },
            {
                "generation": 3,
                "source": "code_002",
                "selected": {
                    "node_id": "code_003",
                    "rule": "constant_plus_one"
                }
            }
        ]
    }
)


memory = TrajectoryMemory(graph)


print()
print("=== TRAJETÓRIA APRENDIDA ===")

trajectories = (
    memory.successful_trajectories()
)

for trajectory in trajectories:

    print(
        trajectory["experience_id"],
        "|",
        " -> ".join(
            trajectory["path"]
        )
    )


print()
print("=== PRÓXIMO PASSO ===")

suggestions = memory.next_steps(
    ["sub_to_add"]
)

for rule, count in suggestions.items():

    print(
        rule,
        "| ocorrências=",
        count
    )


print()
print("=== MELHOR CAMINHO ===")

best = memory.best_path()

if best:

    print(
        " -> ".join(
            best["path"]
        )
    )

else:

    print(
        "Nenhum caminho encontrado."
    )


print()
print("MEMÓRIA DE TRAJETÓRIA: OK")
