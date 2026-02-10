from dataclasses import dataclass

LFSR_KEY = 0x9A8B3C6D  # std_logic_vector(31 downto 0) := x"9A8B3C6D"

def get_bit(value: int, idx: int) -> int:
    return (value >> idx) & 1

def set_bit(value: int, idx: int, bit: int) -> int:
    if bit:
        return value | (1 << idx)
    else:
        return value & ~(1 << idx)

def slice_bits(value: int, hi: int, lo: int) -> int:
    mask = (1 << (hi - lo + 1)) - 1
    return (value >> lo) & mask

def assign_slice(dst: int, hi: int, lo: int, src: int) -> int:
    width = hi - lo + 1
    mask = ((1 << width) - 1) << lo
    dst &= ~mask
    dst |= (src << lo) & mask
    return dst


@dataclass
class RawEncodeDecode:
    # lfsr(0..3) each 32-bit
    lfsr: list
    sel_lfsr: int
    lfsr_int_en: int

    def __init__(self):
        self.lfsr = [LFSR_KEY, LFSR_KEY, LFSR_KEY, LFSR_KEY]
        self.sel_lfsr = 0
        self.lfsr_int_en = 0

    def reset_or_init(self):
        self.lfsr = [LFSR_KEY, LFSR_KEY, LFSR_KEY, LFSR_KEY]

    def lfsr_0_rotate(self):
        if self.sel_lfsr != 0:
            return
        v = self.lfsr[0]

        # Start from original v and build new_v
        new_v = 0

        # lfsr(0)(31 downto 22) <= lfsr(0)(30 downto 21);
        new_v = assign_slice(new_v, 31, 22, slice_bits(v, 30, 21))

        # lfsr(0)(21) <= lfsr(0)(31) xor lfsr(0)(20);
        bit21 = get_bit(v, 31) ^ get_bit(v, 20)
        new_v = set_bit(new_v, 21, bit21)

        # lfsr(0)(20 downto 16) <= lfsr(0)(19 downto 15);
        new_v = assign_slice(new_v, 20, 16, slice_bits(v, 19, 15))

        # lfsr(0)(15) <= lfsr(0)(31) xor lfsr(0)(14);
        bit15 = get_bit(v, 31) ^ get_bit(v, 14)
        new_v = set_bit(new_v, 15, bit15)

        # lfsr(0)(14 downto 12) <= lfsr(0)(13 downto 11);
        new_v = assign_slice(new_v, 14, 12, slice_bits(v, 13, 11))

        # lfsr(0)(11) <= lfsr(0)(31) xor lfsr(0)(10);
        bit11 = get_bit(v, 31) ^ get_bit(v, 10)
        new_v = set_bit(new_v, 11, bit11)

        # lfsr(0)(10) <= lfsr(0)(9);
        new_v = set_bit(new_v, 10, get_bit(v, 9))

        # lfsr(0)(9) <= lfsr(0)(31) xor lfsr(0)(8);
        bit9 = get_bit(v, 31) ^ get_bit(v, 8)
        new_v = set_bit(new_v, 9, bit9)

        # lfsr(0)(8) <= lfsr(0)(7);
        new_v = set_bit(new_v, 8, get_bit(v, 7))

        # lfsr(0)(7) <= lfsr(0)(31) xor lfsr(0)(6);
        bit7 = get_bit(v, 31) ^ get_bit(v, 6)
        new_v = set_bit(new_v, 7, bit7)

        # lfsr(0)(6 downto 1) <= lfsr(0)(5 downto 0);
        new_v = assign_slice(new_v, 6, 1, slice_bits(v, 5, 0))

        # lfsr(0)(0) <= lfsr(0)(31);
        new_v = set_bit(new_v, 0, get_bit(v, 31))

        self.lfsr[0] = new_v & 0xFFFFFFFF

    def lfsr_1_rotate(self):
        if self.sel_lfsr != 1:
            return
        v = self.lfsr[1]
        new_v = 0

        new_v = assign_slice(new_v, 31, 28, slice_bits(v, 30, 27))
        bit27 = get_bit(v, 31) ^ get_bit(v, 26)
        new_v = set_bit(new_v, 27, bit27)
        new_v = assign_slice(new_v, 26, 24, slice_bits(v, 25, 23))
        bit23 = get_bit(v, 31) ^ get_bit(v, 22)
        new_v = set_bit(new_v, 23, bit23)
        new_v = assign_slice(new_v, 22, 14, slice_bits(v, 21, 13))
        bit13 = get_bit(v, 31) ^ get_bit(v, 12)
        new_v = set_bit(new_v, 13, bit13)
        new_v = set_bit(new_v, 12, get_bit(v, 11))
        bit11 = get_bit(v, 31) ^ get_bit(v, 10)
        new_v = set_bit(new_v, 11, bit11)
        new_v = assign_slice(new_v, 10, 6, slice_bits(v, 9, 5))
        bit5 = get_bit(v, 31) ^ get_bit(v, 4)
        new_v = set_bit(new_v, 5, bit5)
        new_v = assign_slice(new_v, 4, 1, slice_bits(v, 3, 0))
        new_v = set_bit(new_v, 0, get_bit(v, 31))

        self.lfsr[1] = new_v & 0xFFFFFFFF

    def lfsr_2_rotate(self):
        if self.sel_lfsr != 2:
            return
        v = self.lfsr[2]
        new_v = 0

        new_v = assign_slice(new_v, 31, 24, slice_bits(v, 30, 23))
        bit23 = get_bit(v, 31) ^ get_bit(v, 22)
        new_v = set_bit(new_v, 23, bit23)
        new_v = assign_slice(new_v, 22, 18, slice_bits(v, 21, 17))
        bit17 = get_bit(v, 31) ^ get_bit(v, 16)
        new_v = set_bit(new_v, 17, bit17)
        new_v = set_bit(new_v, 16, get_bit(v, 15))
        bit15 = get_bit(v, 31) ^ get_bit(v, 14)
        new_v = set_bit(new_v, 15, bit15)
        new_v = assign_slice(new_v, 14, 8, slice_bits(v, 13, 7))
        bit7 = get_bit(v, 31) ^ get_bit(v, 6)
        new_v = set_bit(new_v, 7, bit7)
        new_v = assign_slice(new_v, 6, 4, slice_bits(v, 5, 3))
        bit3 = get_bit(v, 31) ^ get_bit(v, 2)
        new_v = set_bit(new_v, 3, bit3)
        new_v = assign_slice(new_v, 2, 1, slice_bits(v, 1, 0))
        new_v = set_bit(new_v, 0, get_bit(v, 31))

        self.lfsr[2] = new_v & 0xFFFFFFFF

    def lfsr_3_rotate(self):
        if self.sel_lfsr != 3:
            return
        v = self.lfsr[3]
        new_v = 0

        new_v = assign_slice(new_v, 31, 26, slice_bits(v, 30, 25))
        bit25 = get_bit(v, 31) ^ get_bit(v, 24)
        new_v = set_bit(new_v, 25, bit25)
        new_v = assign_slice(new_v, 24, 18, slice_bits(v, 23, 17))
        bit17 = get_bit(v, 31) ^ get_bit(v, 16)
        new_v = set_bit(new_v, 17, bit17)
        new_v = assign_slice(new_v, 16, 15, slice_bits(v, 15, 14))
        bit14 = get_bit(v, 31) ^ get_bit(v, 13)
        new_v = set_bit(new_v, 14, bit14)
        new_v = assign_slice(new_v, 13, 10, slice_bits(v, 12, 9))
        bit9 = get_bit(v, 31) ^ get_bit(v, 8)
        new_v = set_bit(new_v, 9, bit9)
        bit8 = get_bit(v, 31) ^ get_bit(v, 7)
        new_v = set_bit(new_v, 8, bit8)
        new_v = assign_slice(new_v, 7, 1, slice_bits(v, 6, 0))
        new_v = set_bit(new_v, 0, get_bit(v, 31))

        self.lfsr[3] = new_v & 0xFFFFFFFF

    def tick(
        self,
        reset: int,
        init: int,
        lfsr_en: int,
        data_in: int,
        encode_enable: int,
    ) -> int:
        """
        Simulate one rising_edge(clk) of the VHDL.

        reset, init, lfsr_en, encode_enable: 0/1
        data_in: 32-bit int
        Returns data_out (32-bit int)
        """

        # data_out combinational
        if encode_enable == 0:
            data_out = data_in & 0xFFFFFFFF
        else:
            data_out = (data_in ^ self.lfsr[self.sel_lfsr]) & 0xFFFFFFFF

        # LFSR_CONTROL_PROCESS
        if reset == 1 or init == 1:
            # sel_lfsr <= to_integer(unsigned(data_out(11 downto 10)));
            self.sel_lfsr = slice_bits(data_out, 11, 10)
            self.lfsr_int_en = self.sel_lfsr
        elif lfsr_en == 1:
            self.lfsr_int_en = self.sel_lfsr
            self.sel_lfsr = slice_bits(data_out, 11, 10)

        # LFSR_x_ROTATE_PROCESS blocks
        if reset == 1 or init == 1:
            self.reset_or_init()
        else:
            self.lfsr_0_rotate()
            self.lfsr_1_rotate()
            self.lfsr_2_rotate()
            self.lfsr_3_rotate()

        return data_out & 0xFFFFFFFF
