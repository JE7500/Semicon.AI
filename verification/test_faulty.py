
from pathlib import Path

from verification.engine import VerificationEngine


ROOT = Path(__file__).resolve().parent


def main():
    engine = VerificationEngine(timeout_seconds=30)

    result = engine.verify(
        rtl_file=ROOT / "tests" / "fixtures" / "counter_faulty.v",
        testbench_file=ROOT / "testbench" / "counter_4bit_tb.v",
    )

    print("=== Fault Detection Test ===")
    print(f"Status: {result['status']}")

    print("\nSimulation output:")
    print(result["simulation_output"])

    if result["status"] == "functional_failed":
        print("FAULT DETECTION TEST PASSED")
    else:
        print("FAULT DETECTION TEST FAILED")


if __name__ == "__main__":
    main()
