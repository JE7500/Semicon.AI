
import numpy as np
import pytest

from fl.clients.simulated_client import create_simulated_client
from fl.coordinator.server import run_federated_round


def test_three_client_federated_round():
    clients = [
        create_simulated_client("A", 100, 1.0),
        create_simulated_client("B", 200, 2.0),
        create_simulated_client("C", 300, 3.0),
    ]

    result = run_federated_round(clients)

    assert result["round"] == 1
    assert result["client_count"] == 3
    assert result["total_samples"] == 600

    np.testing.assert_allclose(
        result["aggregated_state"]["lora_A"],
        np.full((2, 2), 2.3333333, dtype=np.float32),
    )


def test_client_updates_remain_unchanged():
    clients = [
        create_simulated_client("A", 100, 1.0),
        create_simulated_client("B", 200, 2.0),
    ]

    originals = [
        client.get_update() for client in clients
    ]

    run_federated_round(clients)

    for client, original in zip(clients, originals):
        for name, tensor in original.items():
            np.testing.assert_array_equal(
                client.local_state[name],
                tensor,
            )


def test_rejects_empty_client_list():
    with pytest.raises(ValueError):
        run_federated_round([])


def test_rejects_duplicate_client_ids():
    clients = [
        create_simulated_client("Company_A", 100, 1.0),
        create_simulated_client("Company_A", 200, 2.0),
    ]

    with pytest.raises(ValueError):
        run_federated_round(clients)


def test_custom_round_number():
    clients = [
        create_simulated_client("A", 100, 1.0),
        create_simulated_client("B", 200, 2.0),
    ]

    result = run_federated_round(clients, round_number=5)

    assert result["round"] == 5


@pytest.mark.parametrize("round_number", [0, -1, 1.5, True, "2"])
def test_rejects_invalid_round_numbers(round_number):
    clients = [
        create_simulated_client("A", 100, 1.0),
    ]

    with pytest.raises(ValueError):
        run_federated_round(clients, round_number=round_number)
