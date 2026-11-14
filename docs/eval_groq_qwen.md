# Evaluasi LLM Cadangan (Groq)

Skor: 7/14
Rata-rata latensi: 11.83 detik

## Tabel Hasil per Kasus

| ID | Bahasa | Uji | PASS/FAIL | Alasan | Latensi (s) | Status HTTP |
|----|--------|-----|-----------|--------|-------------|-------------|
| E1 | en | Past tense error | PASS | PASS | 1.24 | 200 |
| E2 | en | Article error | FAIL | penjelasan bukan bahasa Indonesia | 23.566 | 200 |
| E3 | en | Preposition error | FAIL | penjelasan bukan bahasa Indonesia | 0.945 | 200 |
| E4 | en | Subject-verb agreement error | FAIL | penjelasan bukan bahasa Indonesia | 3.016 | 200 |
| E5 | en | Plural/singular error | FAIL | API error: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) | 44.802 | - |
| E6 | en | Word order error | FAIL | penjelasan bukan bahasa Indonesia | 1.292 | 200 |
| C1 | en | Correct sentence 1 | PASS | PASS | 0.442 | 200 |
| C2 | en | Correct sentence 2 | PASS | PASS | 1.519 | 200 |
| C3 | en | Correct sentence 3 | FAIL | API error: HTTPSConnectionPool(host='api.groq.com', port=443): Read timed out. (read timeout=30) | 31.201 | - |
| Z1 | zh | Mandarin 1 | PASS | PASS | 1.238 | 200 |
| Z2 | zh | Mandarin 2 | PASS | PASS | 4.634 | 200 |
| J1 | ja | Japanese 1 | PASS | PASS | 2.285 | 200 |
| J2 | ja | Japanese 2 | FAIL | API error: HTTPSConnectionPool(host='api.groq.com', port=443): Read timed out. (read timeout=30) | 34.522 | - |
| M1 | en | Code mixing | PASS | PASS | 14.895 | 200 |

## Ringkasan Skor
- Total kasus: 14
- Lulus: 7
- Gagal: 7
- Rata-rata latensi: 11.83 detik

## Daftar FAIL
- E2 (Article error): penjelasan bukan bahasa Indonesia
- E3 (Preposition error): penjelasan bukan bahasa Indonesia
- E4 (Subject-verb agreement error): penjelasan bukan bahasa Indonesia
- E5 (Plural/singular error): API error: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
- E6 (Word order error): penjelasan bukan bahasa Indonesia
- C3 (Correct sentence 3): API error: HTTPSConnectionPool(host='api.groq.com', port=443): Read timed out. (read timeout=30)
- J2 (Japanese 2): API error: HTTPSConnectionPool(host='api.groq.com', port=443): Read timed out. (read timeout=30)

## 3 Contoh Jawaban Mentah Paling Buruk

### E5 - Plural/singular error
- Pesan pengguna: I have two book
- Status HTTP: -
- Error: API error: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
- Latensi: 44.802 detik
```
Tidak ada respons mentah (koneksi ditutup paksa oleh server).
```

### C3 - Correct sentence 3
- Pesan pengguna: The weather is very nice today.
- Status HTTP: -
- Error: API error: HTTPSConnectionPool(host='api.groq.com', port=443): Read timed out. (read timeout=30)
- Latensi: 31.201 detik
```
Tidak ada respons mentah (timeout baca 30 detik).
```

### J2 - Japanese 2
- Pesan pengguna: Watashi wa gakusei desu
- Status HTTP: -
- Error: API error: HTTPSConnectionPool(host='api.groq.com', port=443): Read timed out. (read timeout=30)
- Latensi: 34.522 detik
```
Tidak ada respons mentah (timeout baca 30 detik).
```

## Catatan
- Tidak ada API key yang tercantum dalam laporan ini.
- Semua pemanggilan API menggunakan `requests` ke endpoint Groq.
- System prompt menggunakan `_build_system_prompt` dari `services/llm.py` yang sama dengan Gemini.