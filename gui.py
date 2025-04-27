import os
import streamlit as st
from mini_aes import (
    derive_key16, text_to_blocks, blocks_to_text,
    encrypt_block, decrypt_block,
    cbc_encrypt_blocks, cbc_decrypt_blocks,
    ecb_encrypt_blocks, ecb_decrypt_blocks,
    save_log_txt, save_blocks_csv,
    load_txt, load_blocks_csv
)

st.title("Mini-AES Text Encryptor/Decryptor")

mode = st.radio("Mode", ["Encrypt", "Decrypt"])
op   = st.selectbox("Mode of Operation", ["Default", "ECB", "CBC"])
inp_src = st.radio("Input dari", ["Text langsung", "Upload file"])

# **DI SINI**: definisikan variabel `input_text` SELALU
if inp_src == "Upload file":
    upload = st.file_uploader("Pilih .txt (plaintext) atau .csv (cipher blocks)")
    input_text = None
else:
    # Karena Text langsung, kita tampilkan text_area sekarang juga
    if mode == "Encrypt":
        # Kalau encrypt, area untuk plaintext
        input_text = st.text_area("Plaintext", height=150)
    else:
        # Kalau decrypt, area untuk ciphertext (HEX)
        input_text = st.text_area("Ciphertext (HEX, kelipatan 4)", height=150)
    upload = None

# Passphrase & IV
passphrase = st.text_input("Passphrase", type="password")
if op == "CBC":
    iv_hex = st.text_input("IV (4-digit HEX, misal 1A2B)", value="0000")
    try:
        iv = int(iv_hex, 16)
    except ValueError:
        st.error("IV harus 4-digit HEX!")
        st.stop()
else:
    iv = 0

# Tombol Run
if st.button("Run"):
    if not passphrase:
        st.error("Passphrase wajib diisi")
        st.stop()

    key = text_to_blocks(passphrase)[0]

    # BACA INPUT: kalau upload, baca file; kalau text, pakai `input_text`
    if inp_src == "Upload file":
        if upload is not None:
            raw = upload.getvalue().decode("utf-8")
        else:
            st.error("File harus dipilih terlebih dahulu.")
            st.stop()
    else:
        raw = input_text

    # Pastikan `raw` tidak kosong
    if not raw:
        st.error("Masukkan plaintext/ciphertext terlebih dahulu")
        st.stop()

    # --- ENCRYPT ---
    if mode == "Encrypt":
        blocks = text_to_blocks(raw)
        if op == "Default":
            ct_blocks = [encrypt_block(b, key) for b in blocks]
        elif op == "ECB":
            ct_blocks = ecb_encrypt_blocks(blocks, key)
        else:  
            ct_blocks = cbc_encrypt_blocks(blocks, key, iv)
        hex_ct = "".join(f"{b:04X}" for b in ct_blocks)
        st.code(f"Ciphertext (HEX): {hex_ct}")

        # Save results and log
        save_log_txt("log.txt", " Input (Plaintext):", raw, "\n", "Output (Ciphertext):", hex_ct, "\n")
        save_blocks_csv("cipher_blocks.csv", ct_blocks)

    # --- DECRYPT ---
    else:
        # Validasi kelipatan 4 untuk hex
        raw = raw.strip()
        if len(raw) % 4 != 0:
            st.error("Ciphertext HEX harus kelipatan 4")
            st.stop()

        blocks = [int(raw[i:i+4], 16) for i in range(0, len(raw), 4)]
        
        if op == "ECB":
            pt_blocks = ecb_decrypt_blocks(blocks, key)
        elif op == "CBC":
            pt_blocks = cbc_decrypt_blocks(blocks, key, iv)
        else:
            pt_blocks = [decrypt_block(b, key) for b in blocks]

        text = blocks_to_text(pt_blocks)
        st.code(f"Plaintext: {text}")

        # Save results and log
        save_log_txt("log.txt", " Input (Ciphertext):", raw, "\n", "Output (Plaintext):", text, "\n")
        save_blocks_csv("plaintext_blocks.csv", pt_blocks)

    with open("log.txt", "r") as log_file:
        st.download_button("Download Log", log_file, file_name="log.txt")

    with open("cipher_blocks.csv" if mode == "Encrypt" else "plaintext_blocks.csv", "r") as output_file:
        st.download_button("Download Output CSV", output_file, file_name="output.csv")
