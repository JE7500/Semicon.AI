
from pathlib import Path

import pytest

from verification.engine import VerificationEngine


ROOT = Path(__file__).resolve().parents[1]
RTL = ROOT / "rtl" / "counter_4bit.v"
TESTBENCH = ROOT / "testbench" / "counter_4bit_tb.v"
FAULTY_RTL = ROOT / "tests" / "fixtures" / "counter_faulty.v"


def test_reference_counter_passes():
    engine = VerificationEngine(timeout_seconds=30)

    result = engine.verify(RTL, TESTBENCH)

    assert result["status"] == "passed"
    assert "ALL TESTS PASSED" in result["simulation_output"]


def test_faulty_counter_is_detected():
    engine = VerificationEngine(timeout_seconds=30)

    result = engine.verify(FAULTY_RTL, TESTBENCH)

    assert result["status"] == "functional_failed"
    assert "TESTS FAILED" in result["simulation_output"]
    assert "FAIL:" in result["simulation_output"]


def test_missing_rtl_is_rejected():
    engine = VerificationEngine(timeout_seconds=30)

    with pytest.raises(FileNotFoundError):
        engine.verify(
            ROOT / "rtl" / "missing_module.v",
            TESTBENCH,
        )


def test_missing_testbench_is_rejected():
    engine = VerificationEngine(timeout_seconds=30)

    with pytest.raises(FileNotFoundError):
        engine.verify(
            RTL,
            ROOT / "testbench" / "missing_testbench.v",
        )


@pytest.mark.parametrize("timeout", [0, -1, 1.5, True])
def test_invalid_timeout_is_rejected(timeout):
    with pytest.raises(ValueError):
        VerificationEngine(timeout_seconds=timeout)


def test_syntax_error_is_rejected(tmp_path):
    engine = VerificationEngine(timeout_seconds=30)

    invalid_rtl = tmp_path / "invalid_rtl.v"
    invalid_rtl.write_text(
        "module broken(input wire clk; endmodule",
        encoding="utf-8",
    )

    result = engine.verify(invalid_rtl, TESTBENCH)

    assert result["status"] == "compile_failed"
    assert result["compile_output"]
    assert result["simulation_output"] == ""


def test_simulation_timeout_is_enforced(tmp_path):
    engine = VerificationEngine(timeout_seconds=2)

    rtl = tmp_path / "simple.v"
    testbench = tmp_path / "hanging_tb.v"

    rtl.write_text(
        "module simple(input wire clk); endmodule",
        encoding="utf-8",
    )

    testbench.write_text(
        """
        module hanging_tb;
            reg clk = 0;
            simple dut(.clk(clk));
            always #1 clk = ~clk;
        endmodule
        """,
        encoding="utf-8",
    )

    result = engine.verify(rtl, testbench)

    assert result["status"] == "simulation_timeout"
