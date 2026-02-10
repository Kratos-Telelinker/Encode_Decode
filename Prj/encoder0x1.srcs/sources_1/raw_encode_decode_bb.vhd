--// +FHDR ---------------------------------------------------------------------------------------------------
--// Copyright Telelinker 2015
--// All rights reserved Telelinker Confidential Proprietary
--// ---------------------------------------------------------------------------------------------------------
--// FILENAME             : raw_encode_decode.vhd
--// DEPARTMENT           : FPGA Development
--// AUTHOR               : B. Balla
--// AUTHOR'S EMAIL       : bballa@signalcraft.com
--// ---------------------------------------------------------------------------------------------------------
--// RELEASE HISTORY
--//   VERSION  | DATE (YYYY/MM/DD) |    AUTHOR     | DESCRIPTION
--//     1.0            2016/04/26        BB           Initial 
--// ---------------------------------------------------------------------------------------------------------
--// KEYWORDS : 
--// ---------------------------------------------------------------------------------------------------------
--// PURPOSE : 
--// ---------------------------------------------------------------------------------------------------------
--// DEFINES
--// DEF NAME           : RANGE     : DESCRIPTION            : DEFAULT  : UNITS
--// SPI_CHIPSCOPE      : N/A       : If defined, create     :          :
--//                    :           : instances of ICON and  :          :
--//                    :           : ILA cores.             :          : 
--// ---------------------------------------------------------------------------------------------------------
--// PARAMETERS
--// PARAM NAME      : RANGE     : DESCRIPTION            : DEFAULT  : UNITS
--// **** see parameter declaration for this info ****
--// ---------------------------------------------------------------------------------------------------------
--// REUSE ISSUES
--// Reset Strategy      : 
--// Clock Domains       : 
--// Critical Timing     : 
--// Test Features       : 
--// Asynchronous I/F    : 
--// Scan Methodology    : 
--// Instantiations      : 
--// Synthesizable (y/n) : 
--// Other               : 
--// ---------------------------------------------------------------------------------------------------------
--// Instantiation template:
--/*

--*/
--// ---------------------------------------------------------------------------------------------------------
--// NOTES:
--// lfsr 0 POLYNOMIAL = 1 + x^7 +  x^9 + x^11 + x^15 + x^21 + x^32
--// lfsr 1 POLYNOMIAL = 1 + x^5 + x^11 + x^13 + x^23 + x^27 + x^32
--// lfsr 2 POLYNOMIAL = 1 + x^3 +  x^7 + x^15 + x^17 + x^23 + x^32
--// lfsr 3 POLYNOMIAL = 1 + x^8 +  x^9 + x^14 + x^17 + x^25 + x^32
--// lfsr KEY        = 0x9A8B3C6D 
--// ---------------------------------------------------------------------------------------------------------
--// -FHDR----------------------------------------------------------------------------------------------------



library ieee; 
use ieee.std_logic_1164.all; 
use ieee.numeric_std.all;

entity raw_encode_decode_bb is
   port 
      (
      clk                  : in  std_logic;
      reset                : in  std_logic;
      init                 : in  std_logic;
      encode_enable        : in  std_logic;
      data_valid_in        : in  std_logic;
      data_valid_out       : inout  std_logic;
      data_in              : in  std_logic_vector(31 downto 0);
      data_out             : inout  std_logic_vector(31 downto 0)
      );
end entity;




    
architecture raw_encode_decode_arch of raw_encode_decode_bb is
-----------------------------------------------------------------
-- COMPONENTS

-----------------------------------------------------------------
-- Type Declarations
type LFSR_TYPE     is array(3 downto 0) of STD_LOGIC_VECTOR(31 downto 0); 
type LFSR_BIT_TYPE is array(3 downto 0) of STD_LOGIC; 
-----------------------------------------------------------------
-- SIGNALS
signal lfsr           : LFSR_TYPE;  
signal lfsr_int_en    : integer range 0 to 3;
signal sel_lfsr       : integer range 0 to 3;
signal data_valid_in_reg        :   std_logic;
signal init_reg                 : std_logic_vector(1 downto 0);
signal data_in_reg              :   std_logic_vector(31 downto 0);
signal data_out0             :  std_logic_vector(31 downto 0);
signal data_out1             :  std_logic_vector(31 downto 0);
signal data_out2             :  std_logic_vector(31 downto 0);
signal data_out3             :  std_logic_vector(31 downto 0);
constant LFSR_KEY     : std_logic_vector(31 downto 0) := x"9A8B3C6D"; 

--   function int_calc(DATA :std_logic_vector) return integer is
--      variable sum: integer:= 0;
--      variable inc: integer:= 1;
--
--      begin
--         for index in 0 to (DATA'length) loop
--            if (DATA(index) = '1') then
--                  sum := sum + inc;
--            end if;
--            inc := inc * 2;
--         end loop;
--      return sum;
--   end function;  
   
begin 

   Init_Rising_PROCESS : process (clk)
      begin
         if rising_edge(clk) then
            if (reset = '1' or init = '0') then
               init_reg(1 downto 0) <= "00";
            elsif (init = '1') then
               init_reg(1 downto 0) <= init_reg(0) & init;
         end if;   
       end if;
        end process;

   Data_In_PROCESS : process (clk)
      begin
         if rising_edge(clk) then
            if (reset = '1' or init_reg(1 downto 0) = "00") then
               data_in_reg(31 downto 0) <= (others => '0');
               data_valid_in_reg <= '0';
            else
               data_in_reg(31 downto 0) <= data_in(31 downto 0);
               data_valid_in_reg <= data_valid_in;
         end if;   
       end if;
        end process;
   
   LFSR_0_ROTATE_PROCESS : process (clk)
      begin
         if rising_edge(clk) then
            if (reset = '1' or init_reg(1 downto 0) = "01") then
               lfsr(0)(31 downto 0) <= LFSR_KEY;
            elsif (data_valid_in_reg = '1') then                               -- + x^32
               lfsr(0)(31 downto 22)   <= lfsr(0)(30 downto 21);
               lfsr(0)(21)             <= lfsr(0)(31) xor lfsr(0)(20);     -- + x^21
               lfsr(0)(20 downto 16)   <= lfsr(0)(19 downto 15);   
               lfsr(0)(15)             <= lfsr(0)(31) xor lfsr(0)(14);     -- + x^15
               lfsr(0)(14 downto 12)   <= lfsr(0)(13 downto 11);
               lfsr(0)(11)             <= lfsr(0)(31) xor lfsr(0)(10);     -- + x^11
               lfsr(0)(10)             <= lfsr(0)(9);
               lfsr(0)(9)              <= lfsr(0)(31) xor lfsr(0)(8);      -- + x^9
               lfsr(0)(8)              <= lfsr(0)(7);
               lfsr(0)(7)              <= lfsr(0)(31) xor lfsr(0)(6);      -- + x^7
               lfsr(0)(6 downto 1)     <= lfsr(0)(5 downto 0);
               lfsr(0)(0)              <= lfsr(0)(31);                     -- 1 + 
            end if;   
         end if;   
      end process;
      
   LFSR_1_ROTATE_PROCESS : process (clk)
      begin
         if rising_edge(clk) then
            if (reset = '1' or init_reg(1 downto 0) = "01") then
               lfsr(1)(31 downto 0) <= LFSR_KEY;
            --elsif (data_valid_in_reg = '1') then
            elsif (data_valid_in_reg = '1' ) then                               -- + x^32
               lfsr(1)(31 downto 28)   <= lfsr(1)(30 downto 27);
               lfsr(1)(27)             <= lfsr(1)(31) xor lfsr(1)(26);     -- + x^27
               lfsr(1)(26 downto 24)   <= lfsr(1)(25 downto 23);   
               lfsr(1)(23)             <= lfsr(1)(31) xor lfsr(1)(22);     -- + x^23
               lfsr(1)(22 downto 14)   <= lfsr(1)(21 downto 13);
               lfsr(1)(13)             <= lfsr(1)(31) xor lfsr(1)(12);     -- + x^13
               lfsr(1)(12)             <= lfsr(1)(11);
               lfsr(1)(11)             <= lfsr(1)(31) xor lfsr(1)(10);     -- + x^11
               lfsr(1)(10 downto 6)    <= lfsr(1)(9 downto 5);
               lfsr(1)(5)              <= lfsr(1)(31) xor lfsr(1)(4);      -- + x^5
               lfsr(1)(4 downto 1)     <= lfsr(1)(3 downto 0);
               lfsr(1)(0)              <= lfsr(1)(31);                     -- 1 + 
            end if;   
         end if;   
      end process;      

   LFSR_2_ROTATE_PROCESS : process (clk)
      begin
         if rising_edge(clk) then
            if (reset = '1' or init_reg(1 downto 0) = "01") then
               lfsr(2)(31 downto 0) <= LFSR_KEY;
            --elsif (data_valid_in_reg = '1') then
            elsif (data_valid_in_reg = '1') then                               -- + x^32
               lfsr(2)(31 downto 24)   <= lfsr(2)(30 downto 23);
               lfsr(2)(23)             <= lfsr(2)(31) xor lfsr(2)(22);     -- + x^23
               lfsr(2)(22 downto 18)   <= lfsr(2)(21 downto 17);   
               lfsr(2)(17)             <= lfsr(2)(31) xor lfsr(2)(16);     -- + x^17
               lfsr(2)(16)             <= lfsr(2)(15);
               lfsr(2)(15)             <= lfsr(2)(31) xor lfsr(2)(14);     -- + x^15
               lfsr(2)(14 downto 8)    <= lfsr(2)(13 downto 7);
               lfsr(2)(7)              <= lfsr(2)(31) xor lfsr(2)(6);      -- + x^7
               lfsr(2)(6 downto 4)     <= lfsr(2)(5 downto 3);
               lfsr(2)(3)              <= lfsr(2)(31) xor lfsr(2)(2);      -- + x^3
               lfsr(2)(2 downto 1)     <= lfsr(2)(1 downto 0);
               lfsr(2)(0)              <= lfsr(2)(31);                     -- 1 + 
            end if;   
         end if;   
      end process;      

   LFSR_3_ROTATE_PROCESS : process (clk)
      begin
         if rising_edge(clk) then
            if (reset = '1' or init_reg(1 downto 0) = "01") then
               lfsr(3)(31 downto 0) <= LFSR_KEY;
            --elsif (data_valid_in_reg = '1') then
            elsif (data_valid_in_reg = '1') then                               -- + x^32
               lfsr(3)(31 downto 26)   <= lfsr(3)(30 downto 25);
               lfsr(3)(25)             <= lfsr(3)(31) xor lfsr(3)(24);     -- + x^25
               lfsr(3)(24 downto 18)   <= lfsr(3)(23 downto 17);   
               lfsr(3)(17)             <= lfsr(3)(31) xor lfsr(3)(16);     -- + x^17
               lfsr(3)(16 downto 15)   <= lfsr(3)(15 downto 14);   
               lfsr(3)(14)             <= lfsr(3)(31) xor lfsr(3)(13);     -- + x^14
               lfsr(3)(13 downto 10)   <= lfsr(3)(12 downto 9);
               lfsr(3)(9)              <= lfsr(3)(31) xor lfsr(3)(8);      -- + x^9
               lfsr(3)(8)              <= lfsr(3)(31) xor lfsr(3)(7);      -- + x^8
               lfsr(3)(7 downto 1)     <= lfsr(3)(6 downto 0);
               lfsr(3)(0)              <= lfsr(3)(31);                     -- 1 + 
            end if;   
         end if;   
      end process;      

   data_out(31 downto 0) <=  data_in_reg(31 downto 0) when (encode_enable = '0') else (data_in_reg(31 downto 0) xor lfsr(sel_lfsr)(31 downto 0));
   data_out0(31 downto 0) <=  data_in_reg(31 downto 0) when (encode_enable = '0') else (data_in_reg(31 downto 0) xor lfsr(0)(31 downto 0));
   data_out1(31 downto 0) <=  data_in_reg(31 downto 0) when (encode_enable = '0') else (data_in_reg(31 downto 0) xor lfsr(1)(31 downto 0));
   data_out2(31 downto 0) <=  data_in_reg(31 downto 0) when (encode_enable = '0') else (data_in_reg(31 downto 0) xor lfsr(2)(31 downto 0));
   data_out3(31 downto 0) <=  data_in_reg(31 downto 0) when (encode_enable = '0') else (data_in_reg(31 downto 0) xor lfsr(3)(31 downto 0));
   data_valid_out        <=  data_valid_in_reg;
   sel_lfsr <= to_integer (unsigned (lfsr(3)(1 downto 0)));
--   sel_lfsr <= int_calc(data_out(11 downto 10));
--   LFSR_CONTROL_PROCESS : process (clk)
--      begin
--         if rising_edge(clk) then
--            if (reset = '1' or init_reg(1 downto 0) = "01") then
--               sel_lfsr <= to_integer(unsigned(data_out(11 downto 10)));
--            elsif (encode_enable = '1' and data_valid_in_reg = '1') then
--               sel_lfsr <= to_integer(unsigned(data_out(11 downto 10)));
--         end if;   
--       end if;
--        end process;       
end;