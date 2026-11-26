
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
RTL = ROOT / "rtl" / "counter_4bit.v"
TESTBENCH = ROOT / "testbench" / "counter_4bit_tb.v"
RESULTS = ROOT / "results"
EXECUTABLE = RESULTS / "counter_test.vvp"


def run_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=ROOT.parent,
    )

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}"
        )

    return result


def main():
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")

    if not iverilog or not vvp:
        print("ERROR: Icarus Verilog or VVP was not found in PATH.")
        return 1

    if not RTL.is_file() or not TESTBENCH.is_file():
        print("ERROR: RTL or testbench source file is missing.")
        return 1

    RESULTS.mkdir(exist_ok=True)

    print("=== Semicon.AI RTL Verification ===")
    print("[1/2] Compiling RTL and testbench...")

    try:
        run_command([
            iverilog,
            "-g2012",
            "-Wall",
            "-s",
            "counter_4bit_tb",
            "-o",
            str(EXECUTABLE),
            str(RTL),
            str(TESTBENCH),
        ])

        print("[2/2] Running simulation...")
        simulation = run_command([vvp, str(EXECUTABLE)])

    except RuntimeError as error:
        print(f"VERIFICATION ERROR: {error}")
        return 1

    if "ALL TESTS PASSED" not in simulation.stdout:
        print("VERIFICATION FAILED: Expected success marker was not found.")
        return 1

    if "TESTS FAILED" in simulation.stdout or "FAIL:" in simulation.stdout:
        print("VERIFICATION FAILED: Testbench reported failures.")
        return 1

    print("=== VERIFICATION PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
