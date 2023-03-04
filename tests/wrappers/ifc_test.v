
module ifc_test(CLK,
	   RST_N,

	   din_value,
	   din_en,
	   din_rdy,

	   dout_en,
	   dout_value,
	   dout_rdy,

	   len_value,
	   len_en,
	   len_rdy,

	   cfg_address,
	   cfg_data_in,
	   cfg_op,
	   cfg_en,
	   cfg_data_out,
	   cfg_rdy);
  output reg  CLK;
  input  RST_N;

  // action method din
  input  [7 : 0] din_value;
  input  din_en;
  output din_rdy;

  // actionvalue method dout
  input  dout_en;
  output [7 : 0] dout_value;
  output dout_rdy;

  // action method len
  input  [7 : 0] len_value;
  input  len_en;
  output len_rdy;

  // actionvalue method cfg
  input  [7 : 0] cfg_address;
  input  [31 : 0] cfg_data_in;
  input  cfg_op;
  input  cfg_en;
  output [31 : 0] cfg_data_out;
  output cfg_rdy;
  ifc_add dut(
	  .CLK(CLK),
	  .RST_N(RST_N),
          .din_value(din_value),
          .din_en(din_en),
          .din_rdy(din_rdy),

	   .dout_en(dout_en),
	   .dout_value(dout_value),
	   .dout_rdy(dout_rdy),

	   .len_value(len_value),
	   .len_en(len_en),
	   .len_rdy(len_rdy),

	   .cfg_address(cfg_address),
	   .cfg_data_in(cfg_data_in),
	   .cfg_op(cfg_op),
	   .cfg_en(cfg_en),
	   .cfg_data_out(cfg_data_out),
	   .cfg_rdy(cfg_rdy)
  );

  initial begin
	  $dumpfile("ifc_add.vcd");
	  $dumpvars;
	  CLK=0;
	  forever begin
		  #5 CLK=~CLK;
	  end
  end
  endmodule
