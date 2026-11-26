
import numpy as np
import pytest

from fl.aggregation.fedavg import fedavg


def test_weighted_average():
    client_a = {"weight": np.array([1.0, 2.0])}
    client_b = {"weight": np.array([3.0, 4.0])}

    result = fedavg([client_a, client_b], [1, 3])

    np.testing.assert_allclose(result["weight"], [2.5, 3.5])


def test_single_client():
    client = {"weight": np.array([2.0, 5.0])}

    result = fedavg([client], [10])

    np.testing.assert_array_equal(result["weight"], client["weight"])


def test_client_inputs_are_not_modified():
    client_a = {"weight": np.array([1.0, 2.0])}
    client_b = {"weight": np.array([3.0, 4.0])}

    original_a = client_a["weight"].copy()
    original_b = client_b["weight"].copy()

    fedavg([client_a, client_b], [2, 2])

    np.testing.assert_array_equal(client_a["weight"], original_a)
    np.testing.assert_array_equal(client_b["weight"], original_b)


def test_rejects_mismatched_client_keys():
    client_a = {"weight": np.array([1.0])}
    client_b = {"bias": np.array([2.0])}

    with pytest.raises(ValueError):
        fedavg([client_a, client_b], [1, 1])


def test_rejects_mismatched_tensor_shapes():
    client_a = {"weight": np.array([1.0, 2.0])}
    client_b = {"weight": np.array([3.0])}

    with pytest.raises(ValueError):
        fedavg([client_a, client_b], [1, 1])


def test_rejects_invalid_sample_counts():
    client = {"weight": np.array([1.0])}

    with pytest.raises(ValueError):
        fedavg([client], [0])


def test_rejects_integer_arrays():
    client = {"weight": np.array([1, 2])}

    with pytest.raises(TypeError):
        fedavg([client], [1])
