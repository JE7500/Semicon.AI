
import numpy as np
import pytest

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


def make_clients():
    return [
        create_simulated_client("Company_A", 100, 1.0),
        create_simulated_client("Company_B", 200, 2.0),
        create_simulated_client("Company_C", 300, 3.0),
    ]


def test_global_state_is_updated_across_rounds():
    clients = make_clients()

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

    assert result["rounds_completed"] == 3
    assert len(result["history"]) == 3

    np.testing.assert_allclose(
        result["global_state"]["lora_A"],
        np.full((2, 2), 1.4, dtype=np.float32),
        rtol=1e-5,
    )

    np.testing.assert_allclose(
        result["global_state"]["lora_B"],
        np.full((2, 2), 1.4, dtype=np.float32),
        rtol=1e-5,
    )


def test_initial_global_state_is_not_modified():
    clients = make_clients()

    initial_state = {
        "lora_A": np.zeros((2, 2), dtype=np.float32),
    }

    original = initial_state["lora_A"].copy()

    run_federated_training(
        clients=clients,
        initial_global_state=initial_state,
        rounds=1,
        update_function=synthetic_update,
    )

    np.testing.assert_array_equal(
        initial_state["lora_A"],
        original,
    )


@pytest.mark.parametrize("rounds", [0, -1, 1.5, True, "2"])
def test_invalid_round_count_is_rejected(rounds):
    with pytest.raises(ValueError):
        run_federated_training(
            clients=make_clients(),
            initial_global_state={
                "lora_A": np.zeros((2, 2), dtype=np.float32),
            },
            rounds=rounds,
            update_function=synthetic_update,
        )
