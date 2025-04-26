# Mini AES

| Nama | NRP |
| ---- | :-: |
| Adlya Isriena Aftarisya | 5027231066 |
| Fiorenza Adelia Nalle | 5027231053 |
| Aryasatya Alaauddin | 5027231082 |
| Falisha Tazkia | 5008221076 |

## Flowchart

![Flowchart](https://github.com/user-attachments/assets/2ec59c4b-5a7f-4088-80d9-293b27464198)

## Key Expansion

### Input:

- 1 buah key 16-bit.

### Proses Key Expansion:

1. Split key jadi dua 8-bit kata awal: w0 dan w1.

2. Untuk i = 0 sampai 2:

    - Rotate w[i+1] sebanyak 4 bit.

    - Substitusi nibble hasil rotate dengan S-Box.
    
    - XOR hasil substitusi dengan w[i] dan konstanta RCON[i % len(RCON)] → hasilnya w[i+2].
    
    - XOR w[i+2] dengan w[i+1] → hasilnya w[i+3].

3. Gabungkan berpasangan (w0,w1), (w2,w3), (w4,w5), (w6,w7) menjadi 4 buah round keys (16-bit).

### Output:

- 4 buah round keys (masing-masing 16-bit), dipakai untuk tiap tahap enkripsi/dekripsi.
