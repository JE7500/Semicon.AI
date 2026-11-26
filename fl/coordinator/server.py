

from fl.aggregation.fedavg import fedavg
from fl.clients.simulated_client import SimulatedClient


def run_federated_round(
    clients: list[SimulatedClient],
    round_number: int = 1,
) -> dict:
    if not clients:
        raise ValueError("At least one client is required.")

    if (
        not isinstance(round_number, int)
        or isinstance(round_number, bool)
        or round_number <= 0
    ):
        raise ValueError("Round number must be a positive integer.")

    client_ids = [client.client_id for client in clients]

    if len(client_ids) != len(set(client_ids)):
        raise ValueError("Client IDs must be unique.")

    updates = [client.get_update() for client in clients]
    sample_counts = [client.sample_count for client in clients]

    aggregated_state = fedavg(updates, sample_counts)

    return {
        "round": round_number,
        "client_count": len(clients),
        "total_samples": sum(sample_counts),
        "client_ids": client_ids,
        "aggregated_state": aggregated_state,
    }
