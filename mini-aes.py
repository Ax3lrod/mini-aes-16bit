# S-Box and inverse S-Box (4-bit)
SBOX = [0x9, 0x4, 0xA, 0xB, 0xD, 0x1, 0x8, 0x5,
        0x6, 0x2, 0x0, 0x3, 0xC, 0xE, 0xF, 0x7]
INV_SBOX = [SBOX.index(i) for i in range(16)]

# Helper functions: nibble extraction and recomposition
def split_nibbles(word: int) -> List[int]:
    return [(word >> (4 * i)) & 0xF for i in reversed(range(4))]

def combine_nibbles(nibbles: List[int]) -> int:
    return sum((n & 0xF) << (4 * (3 - i)) for i, n in enumerate(nibbles))

# SubNibbles / SubBytes (4-bit)
def sub_nibbles(state: List[int]) -> List[int]:
    return [SBOX[n] for n in state]

# MixColumns over GF(2^4) with matrix [[1,4],[4,1]]
def gf4_mul(a: int, b: int) -> int:
    # Multiply in GF(2^4) with irreducible x^4 + x + 1 (0x13)
    res = 0
    for i in range(4):
        if (b >> i) & 1:
            res ^= a << i
    # reduce
    for shift in reversed(range(4, 8)):
        if res & (1 << shift):
            res ^= 0x13 << (shift - 4)
    return res & 0xF

def mix_columns(state: List[int]) -> List[int]:
    s0, s1, s2, s3 = state
    c0 = gf4_mul(1, s0) ^ gf4_mul(4, s2)
    c1 = gf4_mul(1, s1) ^ gf4_mul(4, s3)
    c2 = gf4_mul(4, s0) ^ gf4_mul(1, s2)
    c3 = gf4_mul(4, s1) ^ gf4_mul(1, s3)
    return [c0, c1, c2, c3]

# AddRoundKey (XOR)
def add_round_key(state: List[int], key: List[int]) -> List[int]:
    return [s ^ k for s, k in zip(state, key)]