
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


RTL_CODE = """
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


TESTBENCH_CODE = """
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
        else
            $display("PASS: Reset");

        reset_n = 1;
        enable = 1;
        #10;

        if (count !== 1)
            $display("FAIL: Increment");
        else
            $display("PASS: Increment");

        enable = 0;
        #10;

        if (count !== 1)
            $display("FAIL: Hold");
        else
            $display("PASS: Hold");

        $display("ALL TESTS PASSED");
        $finish;
    end
endmodule
"""


def test_verify_endpoint_returns_passed():
    response = client.post(
        "/v1/verify",
        json={
            "rtl_code": RTL_CODE,
            "testbench_code": TESTBENCH_CODE,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "passed"
    assert "PASS: Reset" in result["simulation_output"]
    assert "PASS: Increment" in result["simulation_output"]
    assert "PASS: Hold" in result["simulation_output"]
    assert "ALL TESTS PASSED" in result["simulation_output"]
