
import numpy as np

from fl.clients.simulated_client import create_simulated_client
from fl.coordinator.server import run_federated_round


def main():
    clients = [
        create_simulated_client("Company_A", 100, 1.0),
        create_simulated_client("Company_B", 200, 2.0),
        create_simulated_client("Company_C", 300, 3.0),
    ]

    result = run_federated_round(clients)

    print("=== Semicon.AI Federated Learning Simulation ===")
    print(f"Federated round: {result['round']}")
    print(f"Participating clients: {result['client_count']}")
    print(f"Total samples: {result['total_samples']}")

    print("\nClient contributions:")

    for client in clients:
        contribution = client.sample_count / result["total_samples"]
        print(
            f"{client.client_id}: "
            f"{client.sample_count} samples "
            f"({contribution:.2%})"
        )

    print("\nAggregated model updates:")

    for name, tensor in result["aggregated_state"].items():
        print(f"{name}:")
        print(np.array2string(tensor, precision=4))

    print("\nSimulation completed successfully.")


if __name__ == "__main__":
    main()
