import hashlib
from typing import List
import csv

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

def inv_sub_nibbles(state: List[int]) -> List[int]:
    return [INV_SBOX[n] for n in state]

# MixColumns over GF(2^4) with matrix [[1,4],[4,1]]
def gf4_mul(a: int, b: int) -> int:
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

def inv_mix_columns(state: List[int]) -> List[int]:
    s0, s1, s2, s3 = state
    c0 = gf4_mul(9, s0) ^ gf4_mul(2, s2)
    c1 = gf4_mul(9, s1) ^ gf4_mul(2, s3)
    c2 = gf4_mul(2, s0) ^ gf4_mul(9, s2)
    c3 = gf4_mul(2, s1) ^ gf4_mul(9, s3)
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

def text_to_blocks(s: str) -> list[int]:
    """Encode UTF-8, pad 0x00 bila perlu, split 2 byte per blok 16-bit."""
    b = s.encode('utf-8')
    if len(b) % 2:
        b += b'\x00'
    return [int.from_bytes(b[i:i+2], 'big') 
            for i in range(0, len(b), 2)]

def blocks_to_text(blocks: list[int]) -> str:
    """Gabung blok → bytes → decode, strip padding null."""
    b = b''.join(blk.to_bytes(2, 'big') for blk in blocks)
    return b.rstrip(b'\x00').decode('utf-8', errors='ignore')

# Encrypt satu block (16-bit) menggunakan Mini-AES
def encrypt_block(plaintext: int, key:int) -> int:
    state = split_nibbles(plaintext)
    rks = key_expansion(key)

    print(f"Initial state: {state}")
    # Initial AddRoundKey
    state = add_round_key(state, split_nibbles(rks[0]))
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

        state = add_round_key(state, split_nibbles(rks[i]))
        print(f"After AddRoundKey: {state}")

    return combine_nibbles(state)

# Decrypt single 16-bit block
def decrypt_block(ciphertext: int, key: int) -> int:
    state = split_nibbles(ciphertext)
    rks = key_expansion(key)
    # initial AddRoundKey with last key
    state = add_round_key(state, split_nibbles(rks[3]))
    state = inv_shift_rows(state)
    state = inv_sub_nibbles(state)
    # 2 full inverse rounds
    for rnd in reversed(range(1, 3)):
        state = add_round_key(state, split_nibbles(rks[rnd]))
        state = inv_mix_columns(state)
        state = inv_shift_rows(state)
        state = inv_sub_nibbles(state)
    # final AddRoundKey
    state = add_round_key(state, split_nibbles(rks[0]))
    return combine_nibbles(state)

def ecb_encrypt_blocks(blocks: List[int], key: int) -> List[int]:
    return [encrypt_block(block, key) for block in blocks]

def ecb_decrypt_blocks(blocks: List[int], key: int) -> List[int]:
    return [decrypt_block(block, key) for block in blocks]

def cbc_encrypt_blocks(blocks: List[int], key: int, iv: int) -> List[int]:
    ciphertext = []
    prev_block = iv
    for block in blocks:
        block_to_encrypt = block ^ prev_block
        encrypted_block = encrypt_block(block_to_encrypt, key)
        ciphertext.append(encrypted_block)
        prev_block = encrypted_block  # Update prev_block for next round
    return ciphertext

def cbc_decrypt_blocks(blocks: List[int], key: int, iv: int) -> List[int]:
    plaintext = []
    prev_block = iv
    for block in blocks:
        decrypted_block = decrypt_block(block, key)
        block_to_xor = decrypted_block ^ prev_block
        plaintext.append(block_to_xor)
        prev_block = block  # Update prev_block for next round
    return plaintext                

def save_log_txt(file_name, *args):
    with open(file_name, "a") as f:
        # Concatenate all arguments as a single string
        log_entry = " ".join(str(arg) for arg in args) + "\n"
        f.write(log_entry)

def save_blocks_csv(path: str, blocks: list[int], header: list[str]=None):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        if header: w.writerow(header)
        for b in blocks:
            w.writerow([f"{b:04X}"])

def load_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_blocks_csv(path: str) -> list[int]:
    out = []
    with open(path, newline='') as f:
        r = csv.reader(f)
        for row in r:
            out.append(int(row[0], 16))
    return out

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

        plaintext_block = text_to_blocks(plaintext)
        key_block = text_to_blocks(key)

        print(f"Plaintext '{plaintext}' -> Block: {hex(plaintext_block)}")
        print(f"Key '{key}' -> Block: {hex(key_block)}")

        round_keys = key_expansion(key_block)
        print(f"Round Keys: {[hex(k) for k in round_keys]}")

        ciphertext_block = encrypt_block(plaintext_block, round_keys)
        ciphertext_hex = hex(ciphertext_block)

        print(f"Ciphertext block: {ciphertext_hex}")
        ciphertext_text = blocks_to_text(ciphertext_block)
        print(f"Ciphertext as text: {ciphertext_text.encode('utf-8')}")
        print(f"Expected output format (hex): {ciphertext_hex}")

# uncomment untuk mengetes testcases
if __name__ == "__main__":
    run_tests()
