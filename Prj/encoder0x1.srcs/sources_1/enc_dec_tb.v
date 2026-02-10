// +FHDR ---------------------------------------------------------------------------------------------------
// Copyright SignalCraft Technologies Inc. 2014
// All rights reserved SignalCraft Technologies Inc. Confidential Proprietary
// ---------------------------------------------------------------------------------------------------------
// FILENAME             : bit_scram_tb.v
// DEPARTMENT           : 
// AUTHOR               : 
// AUTHOR'S EMAIL       : bballa@signalcraft.com
// ---------------------------------------------------------------------------------------------------------
// RELEASE HISTORY
// VERSION  | DATE (YYYY/MM/DD) |    AUTHOR     | DESCRIPTION
// 1.0      |       2014 04 15  |      BDB      | Initial Testbench
// ---------------------------------------------------------------------------------------------------------
// KEYWORDS : 
// ---------------------------------------------------------------------------------------------------------
// PURPOSE : To check functionality of of the data randomizer and the data de-scrambler
// ---------------------------------------------------------------------------------------------------------
// DEFINES
// DEF NAME           : RANGE     : DESCRIPTION            : DEFAULT  : UNITS
// SPI_CHIPSCOPE      : N/A       : If defined, create     :          :
//                    :           : instances of ICON and  :          :
//                    :           : ILA cores.             :          : 
// ---------------------------------------------------------------------------------------------------------
// PARAMETERS
// PARAM NAME      : RANGE     : DESCRIPTION            : DEFAULT  : UNITS
// **** see parameter declaration for this info ****
// ---------------------------------------------------------------------------------------------------------
// REUSE ISSUES
// Reset Strategy      : synchronous, active high
// Clock Domains       : clk 
// Critical Timing     : N/A
// Test Features       : none
// Asynchronous I/F    : none
// Scan Methodology    : N/A
// Instantiations      : none
// Synthesizable (y/n) : n
// Other               : N/A
// ---------------------------------------------------------------------------------------------------------
// Instantiation template:
/*

*/
// ---------------------------------------------------------------------------------------------------------
// NOTES:
//
// ---------------------------------------------------------------------------------------------------------


`timescale 1ns/1ps

//-----------------------------------------------------------------------------
// list of defines (see file header for descriptions)
// - comment out individual defines to "undefine" them
//-----------------------------------------------------------------------------

//`define SPI_CHIPSCOPE


module enc_dec_tb 
(
);

   


               
reg system_clk;
reg rst;
reg initialize;
reg encode_enable;
reg [31:0] counter;
reg data_valid_in;

wire [31:0] data_in;
wire data_valid_out,data_valid_out2;
wire [31:0] encoded_data;
wire [31:0] decoded_data;





initial begin
   system_clk <= 1'b0;
   forever #2.50 system_clk <= ~system_clk;
 end




initial begin
   
    rst <= 1'b1;
      encode_enable <= 1'b0; 
      initialize <= 1'b0;
   #10    
    rst <= 1'b0;
      encode_enable <= 1'b1; 
      initialize <= 1'b1;
      
      

   
end   
assign data_in[31:0] = counter[31:0];

raw_encode_decode_bb encoder
   
      (
      .clk                  (system_clk),
      .reset                (rst),
      .init                 (initialize),
      .encode_enable        (encode_enable),
      .data_valid_in        (data_valid_in),
      
      .data_in              (data_in[31:0]),
      .data_valid_out        (data_valid_out),
      .data_out             (encoded_data[31:0])
      );
raw_encode_decode_bb decoder
   
      (
      .clk                  (system_clk),
      .reset                (rst),
      .init                 (initialize),
      .encode_enable        (encode_enable),
      .data_valid_in        (data_valid_out),
      
      .data_in              (encoded_data[31:0]),
      .data_valid_out        (data_valid_out2),
      .data_out             (decoded_data[31:0])
      );


always @(posedge system_clk)
begin
   if (rst)
      begin
         counter[31:0] <= 32'h0000;
      end
   else
      begin
         counter[31:0] <=  counter[31:0] + 32'd1;
      end            

end

always @(posedge system_clk)
begin
   if (rst)
      begin
         data_valid_in <= 1'b0;
      end
   else if (counter[3:0] == 4'b1111)
      begin
         data_valid_in <= 1'b0;
      end            
    else
      begin
         data_valid_in <=  1'b1;
      end   
end



endmodule












