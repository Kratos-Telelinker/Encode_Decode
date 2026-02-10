import numpy as np

class NumpyLFSR:
    """
    High‑performance polynomial‑driven Fibonacci LFSR.
    Uses uint32 and vectorized bit operations.
    """
    def __init__(self, width, poly, seed):
        self.width = width
        self.poly = poly
        self.state = np.uint32(seed)

        # Convert polynomial taps to bit positions (0 = LSB)
        # Example: width=32, tap x^21 → bit index 31-21 = 10
        self.taps = np.array([width - p for p in poly if p != width], dtype=np.uint32)

        # MSB index (bit 31 for 32‑bit LFSR)
        self.msb = np.uint32(width - 1)

    def step(self):
        v = self.state

        # Extract MSB
        msb_val = (v >> self.msb) & 1

        # XOR all tap bits
        tap_vals = (v >> self.taps) & 1
        feedback = np.bitwise_xor.reduce(tap_vals ^ msb_val)

        # Shift left by 1, insert feedback at LSB
        self.state = np.uint32(((v << 1) & 0xFFFFFFFF) | feedback)

        return self.state

    def get_int(self):
        return int(self.state)
class RawEncodeDecodeNumpy:
    def __init__(self):
        self.LFSR_KEY = np.uint32(0x9A8B3C6D)

        # Polynomials extracted from your VHDL tap logic
        self.poly = [
            [32, 21, 15, 11, 9, 7, 0],      # LFSR0
            [32, 27, 23, 13, 11, 5, 0],     # LFSR1
            [32, 23, 17, 15, 7, 3, 0],      # LFSR2
            [32, 25, 17, 14, 9, 8, 0]       # LFSR3
        ]

        # Instantiate 4 NumPy LFSRs
        self.lfsr = [
            NumpyLFSR(32, self.poly[0], self.LFSR_KEY),
            NumpyLFSR(32, self.poly[1], self.LFSR_KEY),
            NumpyLFSR(32, self.poly[2], self.LFSR_KEY),
            NumpyLFSR(32, self.poly[3], self.LFSR_KEY)
        ]

        self.sel_lfsr = 0
        self.lfsr_int_en = 0

    # ---------------------------------------------------------
    # Rising‑edge clock tick
    # ---------------------------------------------------------
    def clock(self, reset, init, lfsr_en, data_in, encode_enable):
        data_in = np.uint32(data_in)

        # ----------------------------
        # RESET / INIT
        # ----------------------------
        if reset or init:
            for i in range(4):
                self.lfsr[i] = NumpyLFSR(32, self.poly[i], self.LFSR_KEY)

            # sel_lfsr = data_out(11 downto 10)
            self.sel_lfsr = int((data_in >> 10) & 0b11)
            self.lfsr_int_en = self.sel_lfsr

        else:
            # ----------------------------
            # LFSR CONTROL PROCESS
            # ----------------------------
            if lfsr_en:
                self.lfsr_int_en = self.sel_lfsr
                self.sel_lfsr = int((data_in >> 10) & 0b11)

            # ----------------------------
            # UPDATE ONLY SELECTED LFSR
            # ----------------------------
            self.lfsr[self.sel_lfsr].step()

        # ----------------------------
        # OUTPUT LOGIC
        # ----------------------------
        if encode_enable == 0:
            return int(data_in)
        else:
            return int(data_in ^ self.lfsr[self.sel_lfsr].get_int())
