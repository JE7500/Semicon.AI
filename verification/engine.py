

from pathlib import Path
import shutil
import subprocess
import tempfile


class VerificationEngine:
    def __init__(self, timeout_seconds=30):
        self.iverilog = shutil.which("iverilog")
        self.vvp = shutil.which("vvp")
        self.timeout_seconds = timeout_seconds

        if not self.iverilog or not self.vvp:
            raise RuntimeError(
                "Icarus Verilog and VVP must be installed and available in PATH."
            )

        if (
            not isinstance(timeout_seconds, int)
            or isinstance(timeout_seconds, bool)
            or timeout_seconds <= 0
        ):
            raise ValueError("Timeout must be a positive integer.")

    def verify(self, rtl_file, testbench_file):
        rtl_path = Path(rtl_file).resolve()
        testbench_path = Path(testbench_file).resolve()

        if not rtl_path.is_file():
            raise FileNotFoundError(f"RTL file not found: {rtl_path}")

        if not testbench_path.is_file():
            raise FileNotFoundError(
                f"Testbench file not found: {testbench_path}"
            )

        with tempfile.TemporaryDirectory(prefix="semicon_verify_") as workspace:
            executable = Path(workspace) / "verification_run.vvp"

            compile_command = [
                self.iverilog,
                "-g2012",
                "-Wall",
                "-o",
                str(executable),
                str(rtl_path),
                str(testbench_path),
            ]

            try:
                compilation = subprocess.run(
                    compile_command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                )
            except subprocess.TimeoutExpired:
                return {
                    "status": "compile_timeout",
                    "compile_output": "",
                    "simulation_output": "",
                }

            if compilation.returncode != 0:
                return {
                    "status": "compile_failed",
                    "compile_output": compilation.stdout + compilation.stderr,
                    "simulation_output": "",
                }

            try:
                simulation = subprocess.run(
                    [self.vvp, str(executable)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                )
            except subprocess.TimeoutExpired:
                return {
                    "status": "simulation_timeout",
                    "compile_output": compilation.stdout + compilation.stderr,
                    "simulation_output": "",
                }

            simulation_output = simulation.stdout + simulation.stderr

            if simulation.returncode != 0:
                status = "simulation_error"
            elif (
                "TESTS FAILED" in simulation_output
                or "FAIL:" in simulation_output
            ):
                status = "functional_failed"
            elif (
                "ALL TESTS PASSED" in simulation_output.upper()
               or "PASS: ALL COUNTER TESTS PASSED" in simulation_output.upper()
           ):
               status = "passed"
            else:
                status = "inconclusive"

            return {
                "status": status,
                "compile_output": compilation.stdout + compilation.stderr,
                "simulation_output": simulation_output,
            }

    def verify_code(self, rtl_code, testbench_code):
        with tempfile.TemporaryDirectory(prefix="semicon_source_") as workspace:
            workspace = Path(workspace)

            rtl_file = workspace / "design.v"
            testbench_file = workspace / "testbench.v"

            rtl_file.write_text(rtl_code, encoding="utf-8")
            testbench_file.write_text(testbench_code, encoding="utf-8")

            return self.verify(rtl_file, testbench_file)