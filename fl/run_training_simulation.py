
import numpy as np

from fl.clients.simulated_client import create_simulated_client
from fl.coordinator.training import run_federated_training


def synthetic_update(client, global_state, round_number):
    deltas = {
        "Company_A": 0.1,
        "Company_B": 0.2,
        "Company_C": 0.3,
    }

    delta = deltas[client.client_id] * round_number

    return {
        name: tensor + delta
        for name, tensor in global_state.items()
    }


def main():
    clients = [
        create_simulated_client("Company_A", 100, 1.0),
        create_simulated_client("Company_B", 200, 2.0),
        create_simulated_client("Company_C", 300, 3.0),
    ]

    initial_state = {
        "lora_A": np.zeros((2, 2), dtype=np.float32),
        "lora_B": np.zeros((2, 2), dtype=np.float32),
    }

    result = run_federated_training(
        clients=clients,
        initial_global_state=initial_state,
        rounds=3,
        update_function=synthetic_update,
    )

    print("=== Semicon.AI Multi-Round FL Simulation ===")
    print(f"Rounds completed: {result['rounds_completed']}")

    for record in result["history"]:
        print(f"Round {record['round']}: {record['client_count']} clients")

    print("\nFinal aggregated state:")

    for name, tensor in result["global_state"].items():
        print(f"{name}:")
        print(np.array2string(tensor, precision=4))

    print("\nSimulation completed successfully.")


if __name__ == "__main__":
    main()
