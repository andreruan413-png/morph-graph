from engine.structure import (
    structural_profile,
    structural_similarity
)

from engine.experience_memory import (
    ExperienceMemory
)

from engine.trajectory_memory import (
    TrajectoryMemory
)


def mutation_statistics(graph):

    stats = []

    for node in graph.nodes.values():

        if node["type"] != "evaluation":
            continue

        data = node["data"]

        target_id = data.get(
            "target_node"
        )

        target = graph.nodes.get(
            target_id
        )

        if not target:
            continue

        mutation = target["data"].get(
            "mutation"
        )

        source_id = target["data"].get(
            "source_node"
        )

        source = graph.nodes.get(
            source_id
        )

        if not mutation or not source:
            continue

        source_code = source["data"].get(
            "code"
        )

        if not source_code:
            continue

        try:

            profile = structural_profile(
                source_code
            )

        except SyntaxError:

            continue

        stats.append({
            "mutation": mutation,
            "profile": profile,
            "success": bool(
                data.get("success")
            ),
            "score": float(
                data.get("score", 0.0)
            )
        })

    return stats


def trajectory_statistics(graph):

    trajectories = []

    for node_id, node in graph.nodes.items():

        if node["type"] != "code":
            continue

        data = node["data"]

        source_id = data.get(
            "source_node"
        )

        mutation = data.get(
            "mutation"
        )

        if not source_id or not mutation:
            continue

        source = graph.nodes.get(
            source_id
        )

        if not source:
            continue

        source_code = source["data"].get(
            "code"
        )

        target_code = data.get(
            "code"
        )

        if not source_code or not target_code:
            continue

        try:

            source_profile = structural_profile(
                source_code
            )

            target_profile = structural_profile(
                target_code
            )

        except SyntaxError:

            continue

        score = None

        for evaluation in graph.nodes.values():

            if evaluation["type"] != "evaluation":
                continue

            evaluation_data = evaluation[
                "data"
            ]

            if (
                evaluation_data.get(
                    "target_node"
                )
                == node_id
            ):

                score = float(
                    evaluation_data.get(
                        "score",
                        0.0
                    )
                )

                break

        if score is None:
            continue

        trajectories.append({
            "source_node": source_id,
            "target_node": node_id,
            "mutation": mutation,
            "source_profile": source_profile,
            "target_profile": target_profile,
            "score": score
        })

    return trajectories


def learned_path_statistics(
    graph,
    prefix=None
):

    memory = TrajectoryMemory(
        graph
    )

    if prefix is None:
        prefix = []

    return memory.next_steps(
        prefix
    )


def rank_candidates(
    graph,
    source_id,
    candidates
):

    source = graph.nodes[
        source_id
    ]

    source_code = source[
        "data"
    ][
        "code"
    ]

    source_profile = structural_profile(
        source_code
    )

    experiences = mutation_statistics(
        graph
    )

    trajectories = trajectory_statistics(
        graph
    )

    experience_memory = ExperienceMemory(
        graph
    )

    trajectory_memory = TrajectoryMemory(
        graph
    )

    memory_priorities = (
        experience_memory.mutation_priority(
            source_code
        )
    )

    ranked = []

    # Caminhos completos já aprendidos.
    successful_paths = (
        trajectory_memory.successful_trajectories()
    )

    # Regras que aparecem como primeiro
    # passo de uma trajetória semelhante.
    first_step_scores = {}

    for trajectory in successful_paths:

        path = trajectory["path"]

        if not path:
            continue

        first_rule = path[0]

        first_step_scores[first_rule] = (
            first_step_scores.get(
                first_rule,
                0.0
            )
            + trajectory["score"]
        )

    for candidate in candidates:

        exact_attempts = 0
        exact_successes = 0
        exact_score = 0.0

        similar_attempts = 0
        similar_successes = 0
        similar_score = 0.0

        best_similarity = 0.0

        trajectory_score = 0.0
        trajectory_count = 0

        for experience in experiences:

            if (
                experience["mutation"]
                != candidate.name
            ):
                continue

            similarity = structural_similarity(
                source_profile,
                experience["profile"]
            )

            if similarity >= 0.999:

                exact_attempts += 1

                if experience["success"]:
                    exact_successes += 1

                exact_score += (
                    experience["score"]
                )

            elif similarity >= 0.70:

                similar_attempts += 1

                if experience["success"]:
                    similar_successes += 1

                similar_score += (
                    experience["score"]
                    * similarity
                )

                best_similarity = max(
                    best_similarity,
                    similarity
                )

        for trajectory in trajectories:

            if (
                trajectory["mutation"]
                != candidate.name
            ):
                continue

            similarity = structural_similarity(
                source_profile,
                trajectory[
                    "source_profile"
                ]
            )

            if similarity < 0.70:
                continue

            trajectory_score += (
                trajectory["score"]
                * similarity
            )

            trajectory_count += 1

        total_attempts = (
            exact_attempts
            + similar_attempts
        )

        total_successes = (
            exact_successes
            + similar_successes
        )

        total_score = (
            exact_score
            + similar_score
        )

        if total_attempts:

            learned_rate = (
                total_successes
                / total_attempts
            )

            learned_score = (
                total_score
                / total_attempts
            )

        else:

            learned_rate = 0.0
            learned_score = 0.0

        if trajectory_count:

            learned_trajectory = (
                trajectory_score
                / trajectory_count
            )

        else:

            learned_trajectory = 0.0

        experience_priority = (
            memory_priorities.get(
                candidate.name,
                0.0
            )
        )

        # Prioridade específica para uma regra
        # que já apareceu no início de um caminho
        # que terminou em solução.
        path_priority = (
            first_step_scores.get(
                candidate.name,
                0.0
            )
        )

        ranked.append({
            "candidate": candidate,
            "attempts": total_attempts,
            "successes": total_successes,
            "success_rate": learned_rate,
            "average_score": learned_score,
            "similarity": best_similarity,
            "trajectory_score": learned_trajectory,
            "trajectory_count": trajectory_count,
            "experience_priority": (
                experience_priority
            ),
            "path_priority": path_priority
        })

    ranked.sort(
        key=lambda item: (
            item["path_priority"],
            item["experience_priority"],
            item["success_rate"],
            item["average_score"],
            item["trajectory_score"],
            item["similarity"],
            item["successes"]
        ),
        reverse=True
    )

    return ranked
