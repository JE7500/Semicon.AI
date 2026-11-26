
from pathlib import Path

from verification.engine import VerificationEngine


ROOT = Path(__file__).resolve().parent


def main():
    engine = VerificationEngine(timeout_seconds=30)

    result = engine.verify(
        rtl_file=ROOT / "rtl" / "counter_4bit.v",
        testbench_file=ROOT / "testbench" / "counter_4bit_tb.v",
    )

    print("=== Semicon.AI Verification Engine Test ===")
    print(f"Status: {result['status']}")

    if result["compile_output"]:
        print("\nCompilation output:")
        print(result["compile_output"])

    if result["simulation_output"]:
        print("\nSimulation output:")
        print(result["simulation_output"])

    if result["status"] == "passed":
        print("ENGINE TEST PASSED")
    else:
        print("ENGINE TEST FAILED")


if __name__ == "__main__":
    main()
