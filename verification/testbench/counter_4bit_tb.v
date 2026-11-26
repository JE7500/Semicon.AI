
`timescale 1ns/1ps

module counter_4bit_tb;

    reg clk;
    reg reset_n;
    reg enable;
    wire [3:0] count;

    integer errors;

    counter_4bit dut (
        .clk(clk),
        .reset_n(reset_n),
        .enable(enable),
        .count(count)
    );

    always #5 clk = ~clk;

    task check_count;
        input [3:0] expected;
        input [255:0] test_name;
        begin
            if (count !== expected) begin
                $display("FAIL: %0s | Expected=%0d Actual=%0d",
                         test_name, expected, count);
                errors = errors + 1;
            end else begin
                $display("PASS: %0s | Count=%0d",
                         test_name, count);
            end
        end
    endtask

    initial begin
        clk = 0;
        reset_n = 1;
        enable = 0;
        errors = 0;

        // Assert asynchronous reset away from clock edge
        #2 reset_n = 0;
        #1 check_count(4'd0, "Asynchronous reset");

        // Release reset and enable counting at falling edge
        @(negedge clk);
        reset_n = 1;
        enable = 1;

        // Increment
        @(posedge clk);
        #1 check_count(4'd1, "First increment");

        @(posedge clk);
        #1 check_count(4'd2, "Second increment");

        // Disable at falling edge
        @(negedge clk);
        enable = 0;

        @(posedge clk);
        #1 check_count(4'd2, "Enable low hold");

        // Re-enable at falling edge
        @(negedge clk);
        enable = 1;

        // Count from 2 to 15
        repeat (13) begin
            @(posedge clk);
            #1;
        end
        check_count(4'd15, "Count reaches 15");

        // Rollover
        @(posedge clk);
        #1 check_count(4'd0, "Rollover from 15 to 0");

        // Assert reset between clock edges
        @(negedge clk);
        #1 reset_n = 0;
        #1 check_count(4'd0, "Mid-cycle asynchronous reset");

        if (errors == 0)
            $display("ALL TESTS PASSED");
        else
            $display("TESTS FAILED: %0d errors", errors);

        $finish;
    end

endmodule
