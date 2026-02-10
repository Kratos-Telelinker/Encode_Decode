def lfsr_step(value: int, taps: list[int]) -> int:
    """
    32-bit LFSR left-shift with XOR feedback.
    taps: list of bit positions (0..31) that XOR into the new LSB.
    """
    # Extract MSB (bit 31)
    msb = (value >> 31) & 1

    # Compute feedback = XOR of all tap bits + MSB
    feedback = msb
    for t in taps:
        feedback ^= (value >> t) & 1

    # Shift left and insert feedback at bit 0
    value = ((value << 1) & 0xFFFFFFFF) | feedback
    return value


LFSR_POLY = {
    0: [21, 15, 11, 9, 7],
    1: [27, 23, 13, 11, 5],
    2: [23, 17, 15, 7, 3],
    3: [25, 17, 14, 9, 8],
}


class RawEncodeDecode:
    def __init__(self):
        self.lfsr = [LFSR_KEY] * 4
        self.sel_lfsr = 0
        self.lfsr_int_en = 0

    def reset_or_init(self):
        self.lfsr = [LFSR_KEY] * 4

    def tick(self, reset, init, lfsr_en, data_in, encode_enable):
        # Combinational output
        if encode_enable == 0:
            data_out = data_in & 0xFFFFFFFF
        else:
            data_out = (data_in ^ self.lfsr[self.sel_lfsr]) & 0xFFFFFFFF

        # LFSR control logic
        if reset == 1 or init == 1:
            self.sel_lfsr = (data_out >> 10) & 0b11
            self.lfsr_int_en = self.sel_lfsr
            self.reset_or_init()
        elif lfsr_en == 1:
            self.lfsr_int_en = self.sel_lfsr
            self.sel_lfsr = (data_out >> 10) & 0b11

        # Rotate only the selected LFSR
        if reset == 0 and init == 0:
            idx = self.sel_lfsr
            taps = LFSR_POLY[idx]
            self.lfsr[idx] = lfsr_step(self.lfsr[idx], taps)

        return data_out
