import hashlib
from typing import List

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

def derive_key16(passphrase: str) -> int:
    """Hash passphrase → ambil 16-bit pertama sebagai key."""
    h = hashlib.sha256(passphrase.encode('utf-8')).digest()
    return int.from_bytes(h[:2], 'big')  # 0…65535

# ShiftRows (swap nibble positions 1 and 3)
def shift_rows(state: List[int]) -> List[int]:
    return [state[0], state[3], state[2], state[1]]

def inv_shift_rows(state: List[int]) -> List[int]:
    return [state[0], state[3], state[2], state[1]]

# Key expansion: 16-bit -> three 16-bit round keys
def key_expansion(key: int) -> List[int]:
    w = [ (key >> 8) & 0xFF, key & 0xFF ]
    RCON = [0x80, 0x30, 0x80]   # bisa tambahkan RCON[2] jika mau, atau ulangi RCON[0]
    for i in range(3):
        temp = ((w[-1] << 4) & 0xFF) | (w[-1] >> 4)
        hi, lo = (temp >> 4) & 0xF, temp & 0xF
        sub = (SBOX[hi] << 4) | SBOX[lo]
        w.append(w[i] ^ RCON[i % len(RCON)] ^ sub)
        w.append(w[i+1] ^ w[-1])
    # combine jadi 4 round-keys
    round_keys = []
    for i in range(0, len(w), 2):
        round_keys.append((w[i] << 8) | w[i+1])
    return round_keys  # sekarang len=4

# ORANG TIGA
# Mengubah plaintext (2 karakter) menjadi 16-bit block
def text_to_block(plaintext: str) -> int:
    assert len(plaintext) == 2, "Plaintext harus terdiri dari 2 karakter."
    return (ord(plaintext[0]) << 8) | ord(plaintext[1])

# Mengubah 16-bit block menjadi plaintext (2 karakter)
def block_to_text(block: int) -> str:
    high = (block >> 8) & 0xFF
    low = block & 0xFF
    return chr(high) + chr(low)

# Encrypt satu block (16-bit) menggunakan Mini-AES
def encrypt_block(plaintext_block: int, round_keys: List[int]) -> int:
    state = split_nibbles(plaintext_block)

    print(f"Initial state: {state}")
    # Initial AddRoundKey
    state = add_round_key(state, split_nibbles(round_keys[0]))
    print(f"After initial AddRoundKey: {state}")

    # 3 rounds
    for i in range(1, 4):
        print(f"\n--- Round {i} ---")
        state = sub_nibbles(state)
        print(f"After SubNibbles: {state}")

        state = shift_rows(state)
        print(f"After ShiftRows: {state}")

        if i != 3:
            state = mix_columns(state)
            print(f"After MixColumns: {state}")

        state = add_round_key(state, split_nibbles(round_keys[i]))
        print(f"After AddRoundKey: {state}")

    return combine_nibbles(state)

# TESTCASES
def run_tests():
    tests = [
        {"plaintext": "AB", "key": "CD"},
        {"plaintext": "12", "key": "34"},
        {"plaintext": "Hi", "key": "Ok"},
    ]

    for idx, test in enumerate(tests, 1):
        print(f"\n\n=== Test Case {idx} ===")
        plaintext = test["plaintext"]
        key = test["key"]

        plaintext_block = text_to_block(plaintext)
        key_block = text_to_block(key)

        print(f"Plaintext '{plaintext}' -> Block: {hex(plaintext_block)}")
        print(f"Key '{key}' -> Block: {hex(key_block)}")

        round_keys = key_expansion(key_block)
        print(f"Round Keys: {[hex(k) for k in round_keys]}")

        ciphertext_block = encrypt_block(plaintext_block, round_keys)
        ciphertext_hex = hex(ciphertext_block)

        print(f"Ciphertext block: {ciphertext_hex}")
        ciphertext_text = block_to_text(ciphertext_block)
        print(f"Ciphertext as text: {ciphertext_text.encode('utf-8')}")
        print(f"Expected output format (hex): {ciphertext_hex}")

# uncomment untuk mengetes testcases
if __name__ == "__main__":
    run_tests()
