
from verification.engine import VerificationEngine


RTL = """
module counter_4bit (
    input wire clk,
    input wire reset_n,
    input wire enable,
    output reg [3:0] count
);
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n)
            count <= 4'b0000;
        else if (enable)
            count <= count + 1'b1;
    end
endmodule
"""


TESTBENCH = """
`timescale 1ns/1ps

module counter_4bit_tb;
    reg clk = 0;
    reg reset_n = 1;
    reg enable = 0;
    wire [3:0] count;

    counter_4bit dut (
        .clk(clk),
        .reset_n(reset_n),
        .enable(enable),
        .count(count)
    );

    always #5 clk = ~clk;

    initial begin
        reset_n = 0;
        #2;
        if (count !== 0)
            $display("FAIL: Reset");

        reset_n = 1;
        enable = 1;
        #10;

        if (count !== 1)
            $display("FAIL: Increment");
        else
            $display("PASS: Increment");

        $finish;
    end
endmodule
"""


def test_verify_code_accepts_source_strings():
    engine = VerificationEngine(timeout_seconds=30)

    result = engine.verify_code(RTL, TESTBENCH)

    assert result["status"] == "inconclusive"
    assert "PASS: Increment" in result["simulation_output"]
    assert "FAIL:" not in result["simulation_output"]
