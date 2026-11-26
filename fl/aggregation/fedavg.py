
from collections.abc import Mapping, Sequence

import numpy as np


def fedavg(
    client_states: Sequence[Mapping[str, np.ndarray]],
    sample_counts: Sequence[int],
) -> dict[str, np.ndarray]:
    if not client_states:
        raise ValueError("At least one client update is required.")

    if len(client_states) != len(sample_counts):
        raise ValueError("Each client must have a sample count.")

    if any(
        not isinstance(count, (int, np.integer))
        or isinstance(count, (bool, np.bool_))
        or count <= 0
        for count in sample_counts
    ):
        raise ValueError("Sample counts must be positive integers.")

    reference_keys = set(client_states[0])

    if not reference_keys:
        raise ValueError("Client updates cannot be empty.")

    for state in client_states:
        if set(state) != reference_keys:
            raise ValueError("Client state keys do not match.")

    total_samples = sum(sample_counts)
    aggregated = {}

    for key in client_states[0]:
        reference = np.asarray(client_states[0][key])

        if not np.issubdtype(reference.dtype, np.floating):
            raise TypeError(f"State entry '{key}' must be floating-point.")

        result = np.zeros_like(reference, dtype=np.float64)

        for state, count in zip(client_states, sample_counts):
            tensor = np.asarray(state[key])

            if tensor.shape != reference.shape:
                raise ValueError(f"Tensor shape mismatch for '{key}'.")

            if tensor.dtype != reference.dtype:
                raise ValueError(f"Tensor dtype mismatch for '{key}'.")

            result += tensor.astype(np.float64) * (count / total_samples)

        aggregated[key] = result.astype(reference.dtype)

    return aggregated
