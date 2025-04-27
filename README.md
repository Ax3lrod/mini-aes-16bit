# Mini AES

| Nama | NRP |
| ---- | :-: |
| Adlya Isriena Aftarisya | 5027231066 |
| Fiorenza Adelia Nalle | 5027231053 |
| Aryasatya Alaauddin | 5027231082 |
| Falisha Tazkia | 5008221076 |

## Spesifikasi Algoritma Mini-AES 16-bit

### Overview

Mini-AES 16-bit adalah varian dari algoritma AES yang disederhanakan, dengan panjang plaintext dan kunci masing-masing 16-bit. Proses enkripsi berlangsung dalam 3 round, di mana operasi tertentu hanya dilakukan pada round pertama dan kedua, sementara round ketiga hanya melibatkan beberapa operasi tertentu tanpa MixColumns.

### Langkah-langkah Enkripsi

1. Key Expansion:
Proses ini menghasilkan round keys dari kunci utama yang akan digunakan dalam setiap round enkripsi.

2. Round 1 dan 2:
    - AddRoundKey: XOR antara plaintext dan round key untuk memulai enkripsi.
    - SubNibbles: Setiap nibble (4-bit) dalam blok plaintext diganti dengan nilai yang dipetakan menggunakan S-Box 4-bit.
    - ShiftRows: Geser baris-baris dalam blok plaintext sesuai dengan aturan tertentu. Dalam Mini-AES 16-bit, ini dapat dianggap sebagai pergeseran sederhana pada blok 16-bit.
    - MixColumns: Operasi matriks dilakukan pada kolom-kolom data menggunakan elemen-elemen dalam ruang Galois GF(2^4). Proses ini mencampur nilai-nilai pada kolom data untuk meningkatkan kekuatan enkripsi.
    - AddRoundKey: XOR lagi antara data yang sudah dimodifikasi dengan round key untuk round ini.

3. Round 3:
    - AddRoundKey: XOR plaintext dengan round key untuk ronde ketiga.
    - SubNibbles: Gantikan setiap nibble dalam blok data dengan nilai yang sesuai dari S-Box 4-bit.
    - ShiftRows: Geser baris-baris dalam blok sesuai dengan aturan ShiftRows, meskipun MixColumns tidak digunakan pada ronde ketiga.
    - AddRoundKey: XOR kembali dengan round key pada ronde ketiga. Tidak ada operasi MixColumns pada ronde ini.

**Output:**
Ciphertext 16-bit yang dihasilkan dari proses enkripsi di atas.

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

## Implementasi dan Penjelasan Testcases

Dalam pengujian mini-AES, dibuat 3 testcases dengan input berupa plaintext dan key masing-masing 16-bit (setara 2 karakter ASCII) dengan tujuan:
1. Memastikan semua fungsi bekerja dengan benar.
2. Menampilkan proses enkripsi dengan mini-AES pada tiap round.
3. Membandingkan hasil akhir berupa ciphertext dengan expected output.

### Pada Test Case 1
- Plaintext: 'AB'
- Plaintext block: 0x4142
- Key: 'CD'
- Key block: 0x4344, dengan langkah-langkah
1. Key expansion, menghasilkan round keys ['0x4344', '0x1e5a', '0x756b', '0xa6fc']
2. Initial AddRoundKey [4, 1, 4, 2] ⊕ [4, 3, 4, 4] → [0, 2, 0, 6]
3. Round 1
   - SubNibbles: [9, 10, 9, 8]
   - ShiftRows: [9, 8, 9, 10]
   - MixColumns: [11, 6, 11, 12]
   - AddRoundKey: [10, 8, 14, 6]
4. Round 2
   - SubNibbles: [0, 6, 15, 8]
   - ShiftRows: [0, 8, 15, 6]
   - MixColumns: [9, 3, 15, 0]
   - AddRoundKey: [14, 6, 9, 11]
5. Round 3 (tanpa MixColumns)
   - SubNibbles: [15, 8, 2, 3]
   - ShiftRows: [15, 3, 2, 8]
   - AddRoundKey: [5, 5, 13, 4]
6. Ciphertext block: 0x55d4 (sama dengan expected output)

### Pada Test Case 2
- Plaintext: '12'
- Plaintext block: 0x3132
- Key: '34'
- Key block: 0x3334, dengan langkah-langkah
1. Key expansion, menghasilkan round keys ['0x3334', '0x685c', '0xc5ad', '0x0854']
2. Initial AddRoundKey [3, 1, 3, 2] ⊕ [3, 3, 3, 4] → [0, 2, 0, 6]
3. Round 1
   - SubNibbles: [9, 10, 9, 8]
   - ShiftRows: [9, 8, 9, 10]
   - MixColumns: [11, 6, 11, 12]
   - AddRoundKey: [13, 14, 14, 0]
4. Round 2
   - SubNibbles: [14, 15, 15, 9]
   - ShiftRows: [14, 9, 15, 15]
   - MixColumns: [7, 0, 2, 13]
   - AddRoundKey: [11, 5, 8, 0]
5. Round 3 (tanpa MixColumns)
   - SubNibbles: [3, 1, 6, 9]
   - ShiftRows: [3, 9, 6, 1]
   - AddRoundKey: [3, 1, 3, 5]
7. Ciphertext block: 0x3135 (sama dengan expected output)

### Pada Test Case 3
- Plaintext: 'Hi'
- Plaintext block: 0x4869
- Key: 'Ok'
- Key block: 0x4f6b, dengan langkah-langkah
1. Key expansion, menghasilkan round keys ['0x4f6b', '0xf79c', '0x996e', '0x8f13']
2. Initial AddRoundKey [4, 8, 6, 9] ⊕ [4, 15, 6, 11] → [0, 7, 0, 2]
3. Round 1
   - SubNibbles: [9, 5, 9, 10]
   - ShiftRows: [9, 10, 9, 5]
   - MixColumns: [11, 13, 11, 11]
   - AddRoundKey: [4, 10, 2, 7]
4. Round 2
   - SubNibbles: [13, 0, 10, 5]
   - ShiftRows: [13, 5, 10, 0]
   - MixColumns: [3, 5, 11, 7]
   - AddRoundKey: [10, 12, 13, 9]
5. Round 3 (tanpa MixColumns)
   - SubNibbles: [0, 12, 14, 2]
   - ShiftRows: [0, 2, 14, 12]
   - AddRoundKey: [8, 13, 15, 15]
6. Ciphertext block: 0x8dff (sama dengan expected output)

Semua testcase menghasilkan ciphertext yang sesuai dengan langkah enkripsi mini-AES, dan semua proses (SubNibbles, ShiftRows, MixColumns, dan AddRoundKey) juga berjalan sesuai spesifikasi, tanpa kesalahan dalam key expansion pada tiap round.

## Analisis Kelebihan dan Keterbatasan Mini-AES

### Kelebihan
- Sederhana dan Mudah Diimplementasikan. Mini-AES dirancang dengan struktur yang sangat sederhana dibandingkan AES standar, dengan blok data dan kunci hanya sepanjang 16-bit. Hal ini membuat algoritma ini sangat mudah untuk dipelajari dan diimplementasikan.
- Ringan dan Efisien: Dengan ukuran blok yang lebih kecil, yaitu 16-bit, Mini-AES jauh lebih ringan dalam hal penggunaan sumber daya dibandingkan dengan AES standar yang menggunakan blok 128-bit. Ini menjadikannya pilihan yang sangat baik untuk perangkat dengan sumber daya terbatas seperti perangkat IoT, sensor, atau sistem tertanam (embedded systems). 
- Cepat: Proses enkripsi dan dekripsi Mini-AES lebih cepat dan memerlukan lebih sedikit sumber daya dibandingkan dengan AES standar (128-bit, 192-bit, atau 256-bit). 
- Mengajarkan Konsep Dasar AES: Struktur Mini-AES yang mempertahankan komponen-komponen utama dari AES (seperti SubNibbles, ShiftRows, MixColumns, dan AddRoundKey) membuatnya sangat bermanfaat sebagai alat bantu pendidikan.

### Keterbatasan
- Keamanan Rendah: Mini-AES menggunakan blok data yang sangat kecil (16-bit), yang membuatnya rentan terhadap serangan brute force. Dengan hanya 65536 kemungkinan kunci (2^16), serangan terhadap kunci dengan metode brute force menjadi lebih mudah dilakukan dibandingkan dengan AES standar.
- Tidak Cocok untuk Aplikasi dengan Keamanan Tinggi: Karena ukuran kunci dan blok yang kecil, Mini-AES tidak cocok digunakan dalam aplikasi yang membutuhkan tingkat keamanan tinggi. AES standar yang menggunakan blok 128-bit dan kunci lebih panjang lebih tahan terhadap serangan.
- Keterbatasan pada Skala Besar: Meskipun Mini-AES sangat efisien untuk blok data kecil, keterbatasan ukuran blok dan kunci menjadikannya tidak ideal untuk penggunaan pada skala besar, terutama ketika data yang lebih besar perlu dienkripsi secara simultan. AES standar dengan ukuran blok 128-bit dapat menangani data yang lebih besar dengan lebih baik.

## Analisis Keamanan dan Avalanche Effect
Efek Avalanche mengacu pada fenomena di mana perubahan kecil (biasanya 1 bit) pada plaintext atau kunci menyebabkan perubahan yang signifikan (hampir setengah) dalam ciphertext. Dalam kriptografi yang baik, efek avalanche ini sangat penting untuk memastikan bahwa ciphertext tidak mengungkapkan pola atau hubungan langsung dengan plaintext. Efek ini meningkatkan keamanan algoritma kriptografi dengan mengurangi kemungkinan untuk menghubungkan ciphertext kembali ke plaintext atau kunci yang digunakan.
Uji sensitivitas terhadap perubahan 1-bit di plaintext dan key:
- Plaintext: "HI", Key: "AB" → Ciphertext: C855
- Plaintext: "HI", Key: "XB" → Ciphertext: C3D9
- Plaintext: "Hx", Key: "AB" → Ciphertext: 2F3C

Hasil analisis uji sensitivitas tersebut:
- Perubahan pada Key (Key "AB" menjadi "XB"): Ciphertext berubah dari C855 menjadi C3D9. Meskipun perubahan pada key hanya satu bit, perubahan pada ciphertext sangat besar. Hal ini menunjukkan bahwa AES (dan varian seperti Mini-AES) memiliki efek avalanche yang sangat kuat.
- Perubahan pada Plaintext (Plaintext "HI" menjadi "Hx"): Ciphertext berubah dari C855 menjadi 2F3C. Meskipun hanya ada satu karakter yang berubah dalam plaintext (yaitu, huruf "I" menjadi "x"), perubahan ini menyebabkan perubahan besar pada ciphertext.

Dalam kedua kasus ini, perubahan kecil di input (baik pada plaintext atau key) menyebabkan perubahan yang signifikan pada ciphertext. Ini adalah ciri khas dari efek avalanche, yang memastikan bahwa setiap bit dari ciphertext bergantung pada hampir semua bit dari plaintext dan kunci.

Secara umum, dalam kriptografi yang baik, kita menginginkan agar satu bit perubahan pada input (baik plaintext maupun key) menghasilkan perubahan besar dan tidak terduga dalam ciphertext. Hal ini menambah kerumitan dalam menganalisis hubungan antara ciphertext dan plaintext, yang merupakan salah satu aspek penting dalam meningkatkan keamanan algoritma.

Efek avalanche membantu mencegah analisis kriptanalisis linear dan diferensial karena membuat hubungan antara bit-bit ciphertext dan inputnya (baik plaintext maupun key) sangat kompleks. Setiap bit perubahan dalam plaintext atau key menghasilkan perubahan yang luas di ciphertext, membuatnya sangat sulit untuk memprediksi atau mengekstrak informasi yang berguna dari ciphertext tanpa kunci yang tepat.

Dengan demikian, pengaruh avalanche ini menambah tingkat keamanan yang signifikan pada algoritma seperti AES atau Mini-AES, memastikan bahwa perubahan kecil dalam input akan menghasilkan ciphertext yang benar-benar berbeda dan tidak terduga.
