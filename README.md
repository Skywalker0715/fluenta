# Fluenta

Aplikasi pembelajaran bahasa Inggris untuk penutur Indonesia dengan chat teks dan suara, koreksi grammar, dan pemrosesan dokumen.

## Ringkasan

Fluenta adalah aplikasi Streamlit untuk belajar bahasa Inggris melalui percakapan dengan tutor AI. Dibuat untuk pemelajar Indonesia yang ingin berlatih bahasa Inggris, dengan dukungan bahasa Mandarin dan Jepang sebagai bahasa belajar. Aplikasi mendukung chat teks dan suara, koreksi grammar dengan penjelasan dalam Bahasa Indonesia, serta halaman untuk terjemahan dan pemrosesan dokumen. Riwayat sesi disimpan di database SQLite lokal.

## Fitur

- Chat teks dan suara dengan tutor AI (Gemini), balasan dapat diutarakan melalui TTS.
- Koreksi grammar dengan penjelasan dalam Bahasa Indonesia (baris "Fix: ...").
- Pilihan bahasa belajar (Inggris, Mandarin, Jepang) dan level (beginner, intermediate, advanced).
- Kirim otomatis saat diam melalui JavaScript yang disuntikkan ke antarmuka Streamlit.
- Riwayat sesi chat tersimpan di SQLite, daftar sesi ditampilkan di sidebar.
- Halaman Dokumen: unggah PDF/DOCX/TXT, terjemahkan atau rangkum, unduh hasil TXT/DOCX.
- Halaman Terjemah: terjemahkan teks dengan model lokal Indonesia-Inggris atau Gemini.

## Tampilan

Screenshot akan ditambahkan.

## Arsitektur

```
UI (Streamlit: app.py, halaman di pages/)
   |
   +-- services/llm.py      -> Google Gemini (ask_tutor, generate_text)
   +-- services/stt.py      -> Deepgram REST (speech_to_text)
   +-- services/tts.py      -> ElevenLabs REST (text_to_speech)
   +-- services/translate.py-> Opus-MT lokal atau Gemini (translate_id_en, translate_text)
   +-- services/docs.py     -> Gemini / python-docx (process_document)
   +-- db.py                -> SQLite (data/app.db)
```

| Layanan | Tanggung jawab |
| llm | Tutor AI via Gemini: jawab chat, koreksi grammar, terjemahan teks. |
| stt | Ubah ucapan menjadi teks via Deepgram REST. |
| tts | Ubah teks menjadi suara MP3 via ElevenLabs REST. |
| translate | Terjemahan Indonesia ke Inggris via model lokal Opus-MT, atau bahasa lain via Gemini. |
| docs | Ekstrak isi dokumen dan terjemahkan atau rangkumkan hasilnya. |

## Teknologi

| Komponen | Teknologi | Tujuan |
| Antarmuka | Streamlit | Antarmuka chat dan halaman aplikasi. |
| LLM | Google Gemini (paket google-genai) | Tutor AI, terjemahan teks, pemrosesan dokumen. |
| STT | Deepgram REST | Transkripsi ucapan menjadi teks. |
| TTS | ElevenLabs REST | Sintesis suara balasan tutor. |
| Terjemahan lokal | transformers, Helsinki-NLP/opus-mt-id-en | Terjemahan Indonesia ke Inggris tanpa API. |
| Database | SQLite (sqlite3 bawaan) | Riwayat sesi chat dan dokumen di data/app.db. |
| Variabel lingkungan | python-dotenv | Memuat kunci API dari file .env. |

## Prasyarat

- Python 3.12
- Kunci API Google AI Studio (Gemini)
- Kunci API Deepgram
- Kunci API ElevenLabs
- Dapat dijalankan di Windows, macOS, dan Linux dengan Python 3.12.

## Instalasi

Buka PowerShell di folder proyek:

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Isi semua kunci API di file `.env` yang baru dibuat, lalu jalankan:

```powershell
.\myenv\Scripts\python.exe -m streamlit run app.py
```

## Konfigurasi

Semua variabel dibaca dari `.env` melalui `os.getenv`. Tidak ada kunci yang ditulis ke dalam kode.

| Variabel | Keterangan |
| GEMINI_API_KEY | Kunci API Google AI Studio untuk Gemini. Wajib diisi. |
| DEEPGRAM_API_KEY | Kunci API Deepgram untuk pengucapan-ke-teks. Wajib diisi. |
| ELEVENLABS_API_KEY | Kunci API ElevenLabs untuk teks-ke-suara. Wajib diisi. |
| GEMINI_MODEL | Model Gemini yang digunakan (contoh: gemini-2.5-flash). Harus merupakan model yang tersedia untuk kunci Anda. Opsional. |
| ELEVEN_VOICE_ID | ID suara ElevenLabs (contoh ID suara premade/bawaan). Akun gratis ElevenLabs tidak dapat menggunakan suara dari perpustakaan melalui API; gunakan ID suara bawaan (premade voice id). Opsional. |

## Penggunaan

- Chat: ketik pesan di kolom input chat, atau rekam suara untuk ditranskripsi terlebih dahulu. Balasan tutor ditampilkan bersama koreksi grammar jika terdapat kesalahan.
- Suara: nyalakan toggle "Balasan bersuara" di sidebar agar balasan tutor diutarakan sebagai audio.
- Bahasa dan level: pilih bahasa belajar dan level kesulitan di sidebar sebelum memulai percakapan.
- Dokumen: buka halaman Dokumen, unggah file, pilih tugas (Terjemahkan atau Rangkum) dan bahasa target, klik Proses, lalu unduh hasil dalam TXT atau DOCX.
- Terjemah: buka halaman Terjemah, masukkan teks, pilih mesin (model lokal Indonesia-Inggris atau Gemini), klik Terjemahkan.

## Struktur proyek

```
Translator/
├── .env
├── .env.example
├── .gitignore
├── AGENTS.md
├── app.py
├── db.py
├── README.md
├── requirements.txt
├── assets/
│   ├── auto_send.js
│   └── icon.png
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PRD.md
│   └── TASKS.md
├── pages/
│   ├── 1_Dokumen.py
│   └── 2_Terjemah.py
└── services/
    ├── __init__.py
    ├── docs.py
    ├── llm.py
    ├── stt.py
    ├── tts.py
    └── translate.py
```

## Batasan yang diketahui

- Kuota gratis Gemini terbatas dan data pengguna diproses oleh Google.
- Kuota gratis ElevenLabs terbatas.
- Fitur kirim otomatis bergantung pada JavaScript yang disuntikkan ke dalam Streamlit dan mengandalkan elemen internal Streamlit, sehingga dapat rusak setelah pembaruan Streamlit.
- Kualitas STT dan TTS untuk Mandarin dan Jepang belum diverifikasi.
- Tidak ada penilaian ucapan (pronunciation scoring).

## Peta jalan

Idea (bukan komitmen):
- Penilaian ucapan (pronunciation scoring).
- Deployment.

## Keamanan

File `.env` tidak boleh dikomit ke repositori. Putar segera setiap kunci API yang telah terpapar.

## Lisensi

Belum ditentukan.
