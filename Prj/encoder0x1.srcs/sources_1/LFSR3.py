import numpy as np

LFSR_KEY = 0x9A8B3C6D

# tap positions excluding MSB (31), which is implicit
LFSR_POLY = {
    0: [21, 15, 11, 9, 7],
    1: [27, 23, 13, 11, 5],
    2: [23, 17, 15, 7, 3],
    3: [25, 17, 14, 9, 8],
}


def lfsr_step_batch(values: np.ndarray, taps: list[int]) -> np.ndarray:
    """
    Vectorized 32-bit LFSR step for many parallel states.

    values: np.ndarray of dtype=np.uint32, shape (N,)
    taps: list of tap bit positions (0..31), MSB (31) is implicit.
    """
    values = values.astype(np.uint32, copy=False)

    # MSB for all streams
    msb = (values >> 31) & np.uint32(1)

    # feedback = msb XOR all tap bits
    feedback = msb.copy()
    for t in taps:
        feedback ^= (values >> np.uint32(t)) & np.uint32(1)

    # shift left and insert feedback at bit 0
    next_values = ((values << np.uint32(1)) & np.uint32(0xFFFFFFFF)) | feedback
    return next_values.astype(np.uint32)


class BatchRawEncodeDecode:
    """
    Batch version of the 4-LFSR engine.

    - lfsr: shape (4, N) uint32, N parallel instances
    - sel_lfsr: shape (N,) uint8, which LFSR index (0..3) per instance
    """

    def __init__(self, batch_size: int):
        self.N = batch_size
        self.lfsr = np.full((4, self.N), LFSR_KEY, dtype=np.uint32)
        self.sel_lfsr = np.zeros(self.N, dtype=np.uint8)
        self.lfsr_int_en = np.zeros(self.N, dtype=np.uint8)

    def reset_or_init(self):
        self.lfsr[:] = np.uint32(LFSR_KEY)

    def tick(
        self,
        reset: np.ndarray,
        init: np.ndarray,
        lfsr_en: np.ndarray,
        data_in: np.ndarray,
        encode_enable: np.ndarray,
    ) -> np.ndarray:
        """
        Vectorized tick over N instances.

        All inputs: shape (N,), dtype=uint8 for control, uint32 for data_in.
        Returns data_out: shape (N,), dtype=uint32.
        """
        reset = reset.astype(np.uint8, copy=False)
        init = init.astype(np.uint8, copy=False)
        lfsr_en = lfsr_en.astype(np.uint8, copy=False)
        encode_enable = encode_enable.astype(np.uint8, copy=False)
        data_in = data_in.astype(np.uint32, copy=False)

        # combinational data_out
        use_plain = (encode_enable == 0)
        data_out = np.where(
            use_plain,
            data_in,
            data_in ^ self.lfsr[self.sel_lfsr, np.arange(self.N)],
        ).astype(np.uint32)

        # control
        rst_or_init = (reset == 1) | (init == 1)

        # sel_lfsr <= data_out(11 downto 10)
        new_sel = ((data_out >> 10) & np.uint32(0b11)).astype(np.uint8)

        # on reset/init
        self.sel_lfsr = np.where(rst_or_init, new_sel, self.sel_lfsr)
        self.lfsr_int_en = np.where(rst_or_init, self.sel_lfsr, self.lfsr_int_en)

        # on lfsr_en
        en_mask = (lfsr_en == 1) & ~rst_or_init
        self.lfsr_int_en = np.where(en_mask, self.sel_lfsr, self.lfsr_int_en)
        self.sel_lfsr = np.where(en_mask, new_sel, self.sel_lfsr)

        # reset/init LFSR contents
        if np.any(rst_or_init):
            self.reset_or_init()

        # rotate only where not reset/init
        active = ~rst_or_init
        if np.any(active):
            idxs = self.sel_lfsr[active]  # which LFSR per active instance
            # group by LFSR index for efficiency
            for lfsr_idx in range(4):
                mask = active & (self.sel_lfsr == lfsr_idx)
                if not np.any(mask):
                    continue
                taps = LFSR_POLY[lfsr_idx]
                self.lfsr[lfsr_idx, mask] = lfsr_step_batch(
                    self.lfsr[lfsr_idx, mask], taps
                )

        return data_out.astype(np.uint32)


"""
USAGE EXAMPLE

N = 1024
engine = BatchRawEncodeDecode(N)

reset = np.zeros(N, dtype=np.uint8)
init = np.zeros(N, dtype=np.uint8)
lfsr_en = np.ones(N, dtype=np.uint8)
encode_enable = np.ones(N, dtype=np.uint8)
data_in = np.arange(N, dtype=np.uint32)

# first cycle with init asserted
init[:] = 1
out0 = engine.tick(reset, init, lfsr_en, data_in, encode_enable)

# subsequent cycles
init[:] = 0
for _ in range(10):
    out = engine.tick(reset, init, lfsr_en, data_in, encode_enable)

"""