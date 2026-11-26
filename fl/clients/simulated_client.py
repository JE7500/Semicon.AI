
from dataclasses import dataclass

import numpy as np


@dataclass
class SimulatedClient:
    client_id: str
    sample_count: int
    local_state: dict[str, np.ndarray]

    def get_update(self) -> dict[str, np.ndarray]:
        return {
            name: tensor.copy()
            for name, tensor in self.local_state.items()
        }


def create_simulated_client(
    client_id: str,
    sample_count: int,
    update_value: float,
) -> SimulatedClient:
    if not client_id.strip():
        raise ValueError("Client ID cannot be empty.")

    if sample_count <= 0:
        raise ValueError("Sample count must be positive.")

    if not np.isfinite(update_value):
        raise ValueError("Update value must be finite.")

    local_state = {
        "lora_A": np.full((2, 2), update_value, dtype=np.float32),
        "lora_B": np.full((2, 2), update_value * 2, dtype=np.float32),
    }

    return SimulatedClient(
        client_id=client_id,
        sample_count=sample_count,
        local_state=local_state,
    )
