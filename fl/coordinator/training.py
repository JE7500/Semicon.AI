

from collections.abc import Callable, Mapping

import numpy as np

from fl.aggregation.fedavg import fedavg
from fl.clients.simulated_client import SimulatedClient


UpdateFunction = Callable[
    [SimulatedClient, Mapping[str, np.ndarray], int],
    dict[str, np.ndarray],
]


def run_federated_training(
    clients: list[SimulatedClient],
    rounds: int,
    initial_global_state: Mapping[str, np.ndarray],
    update_function: UpdateFunction,
) -> dict:
    if not clients:
        raise ValueError("At least one client is required.")

    if (
        not isinstance(rounds, int)
        or isinstance(rounds, bool)
        or rounds <= 0
    ):
        raise ValueError("Rounds must be a positive integer.")

    client_ids = [client.client_id for client in clients]

    if len(client_ids) != len(set(client_ids)):
        raise ValueError("Client IDs must be unique.")

    if not callable(update_function):
        raise TypeError("Update function must be callable.")

    if not isinstance(initial_global_state, Mapping) or not initial_global_state:
        raise ValueError("Initial global state must be a non-empty mapping.")

    global_state = {
        name: np.asarray(tensor).copy()
        for name, tensor in initial_global_state.items()
    }

    sample_counts = [client.sample_count for client in clients]
    history = []

    for round_number in range(1, rounds + 1):
        client_updates = []

        for client in clients:
            client_global_state = {
                name: tensor.copy()
                for name, tensor in global_state.items()
            }

            update = update_function(
                client,
                client_global_state,
                round_number,
            )
            client_updates.append(update)

        global_state = fedavg(client_updates, sample_counts)

        history.append({
            "round": round_number,
            "client_count": len(clients),
            "total_samples": sum(sample_counts),
        })

    return {
        "rounds_completed": rounds,
        "global_state": global_state,
        "history": history,
    }
