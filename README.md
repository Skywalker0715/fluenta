<p align="center">
  <img src="assets/logo.png" alt="Fluenta" width="420">
</p>

<p align="center">
  <b>Teman latihan bahasa asing berbasis AI.</b><br>
  Ngobrol lewat teks atau suara, dapat koreksi grammar dalam bahasa Indonesia.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/Streamlit-1.66%20(diuji)-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit 1.66 (diuji)">
  <img src="https://img.shields.io/badge/Gemini-API-4285F4?logo=googlegemini&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Lisensi-Apache%202.0-D22128" alt="Apache 2.0">
</p>

<p align="center">
  <a href="#fitur">Fitur</a> ·
  <a href="#kenapa-fluenta">Kenapa Fluenta</a> ·
  <a href="#cara-kerja">Cara kerja</a> ·
  <a href="#model-cadangan-dan-privasi">Model cadangan dan privasi</a> ·
  <a href="#mulai-cepat">Mulai cepat</a> ·
  <a href="#konfigurasi">Konfigurasi</a> ·
  <a href="#pengembangan-dan-tes">Pengembangan dan tes</a> ·
  <a href="#batasan-yang-diketahui">Batasan</a> ·
  <a href="#lisensi">Lisensi</a>
</p>

---

## Tentang

Fluenta adalah aplikasi Streamlit untuk berlatih bahasa Inggris lewat percakapan dengan tutor AI. Dibuat untuk pemelajar Indonesia, dengan Mandarin dan Jepang sebagai bahasa belajar tambahan. Kamu bisa mengetik atau berbicara langsung, dan tutor membalas dengan teks dan suara. Kesalahan grammar dan tense dikoreksi lengkap dengan penjelasan berbahasa Indonesia. Kalau model utama (Gemini) kena batas kuota, chat otomatis dialihkan ke model cadangan (Groq) supaya latihan tidak terputus.

## Kenapa Fluenta

- Koreksi dijelaskan dalam bahasa Indonesia, lengkap dengan tag jenis kesalahan.
- Mode ngomong campur: kalimat campuran Indonesia dan Inggris diterima dan ditandai sebagai campur bahasa, bukan dianggap rusak.
- Kesalahanmu dicatat, ditampilkan sebagai pola di halaman Progres, dan bisa dilatih ulang lewat halaman Latihan (kotak Leitner).
- Tiga bahasa: Inggris, Mandarin (dengan pinyin), dan Jepang (dengan romaji), dengan arti dalam bahasa Indonesia.
- Riwayat, koreksi, dan progres disimpan lokal di SQLite. Isi pesan tetap dikirim ke layanan pihak ketiga yang dipakai (Gemini, Deepgram, ElevenLabs, dan Groq bila cadangan aktif). Gratis dan sumber terbuka (Apache 2.0), memakai kuota gratis tiap layanan.

## Fitur

| Fitur | Keterangan |
|---|---|
| Chat teks dan suara | Rekam suara, kirim otomatis saat berhenti bicara, balasan dibacakan |
| Koreksi grammar | Kalimat diperbaiki dan aturannya dijelaskan dalam bahasa Indonesia |
| Banyak bahasa | Inggris, Mandarin (dengan pinyin), dan Jepang (dengan romaji) |
| Tiga level | Beginner, intermediate, dan advanced menyesuaikan panjang dan kerumitan balasan |
| Riwayat sesi | Semua percakapan tersimpan di SQLite dan bisa dibuka lagi |
| Halaman Dokumen | Unggah PDF, DOCX, TXT, atau MD, lalu terjemahkan atau rangkum dan unduh hasilnya sebagai TXT atau DOCX. Cadangan model tersedia opsional (dengan persetujuan) hanya untuk dokumen teks. |
| Halaman Terjemah | Model lokal Indonesia ke Inggris, atau Gemini untuk bahasa lain (dengan fallback ke Groq saat Gemini gagal) |
| Halaman Progres | Statistik belajar, koreksi per hari, dan daftar kesalahan terbaru |
| Pola kesalahan | Grafik dan urutan tag kesalahan yang paling sering terjadi |
| Latihan | Latihan ulang koreksi baru dengan sistem kotak Leitner (kotak 1–5; interval 1, 2, 4, 8, 16 hari; dikuasai di kotak 4 ke atas). |
| Mode ngomong campur | Menerima campuran kata Indonesia dalam pesan tanpa dianggap kesalahan |
| Koreksi terstruktur | Kalimat benar, penjelasan Indonesia, dan tag jenis kesalahan |
| Model cadangan | Chat tetap jalan lewat Groq saat Gemini kena batas kuota; dokumen teks juga bisa diproses lewat cadangan setelah pengguna mengklik "Pakai model cadangan" |

## Cara kerja

```mermaid
flowchart LR
    U([Pengguna]) --> UI["Streamlit<br/>app.py dan views/"]
    UI --> LLM["services/llm.py<br/>Gemini (utama)"]
    UI --> STT["services/stt.py<br/>Deepgram"]
    UI --> TTS["services/tts.py<br/>ElevenLabs"]
    UI --> TR["services/translate.py<br/>Opus-MT lokal / Gemini"]
    UI --> DOC["services/docs.py<br/>Gemini, Groq (cadangan), dan python-docx"]
    UI --> DB[("SQLite<br/>data/app.db")]
    GQ["Groq<br/>gpt-oss-120b (cadangan)"]
    LLM -.->|"cadangan (429, 5xx, timeout, jaringan)"| GQ
    TR -.->|"fallback Groq (teks <= 3000 char)"| GQ
    DOC -.->|"cadangan opsional (persetujuan pengguna)"| GQ
```

Garis putus-putus menunjukkan jalur cadangan: Groq hanya dipanggil kalau Gemini gagal.

Alur percakapan suara:

```
Mikrofon  ->  Deepgram (suara ke teks)  ->  Gemini (tutor dan koreksi)  ->  ElevenLabs (teks ke suara)  ->  Dibacakan
```

| Komponen | Teknologi | Fungsi |
|---|---|---|
| Antarmuka | Streamlit | Chat, navigasi, dan halaman aplikasi |
| Tutor dan dokumen | Google Gemini (`google-genai`) | Balasan, koreksi, terjemahan, ringkasan |
| Suara ke teks | Deepgram | Transkripsi ucapan |
| Teks ke suara | ElevenLabs | Suara balasan tutor |
| Terjemahan lokal | `transformers`, `Helsinki-NLP/opus-mt-id-en` | Indonesia ke Inggris tanpa API |
| Penyimpanan | SQLite | Riwayat sesi, dokumen, dan statistik |
| Model cadangan | Groq (`openai/gpt-oss-120b`) | Cadangan untuk chat tutor, terjemahan teks pendek (jalur Gemini di halaman Terjemah), dan dokumen teks (opsional, setelah persetujuan) saat Gemini gagal |

### Alur model cadangan

```
Pesan pengguna -> Gemini -> sukses -> balasan
                          -> gagal (429, 5xx, timeout, jaringan) -> Groq -> balasan + label "Dijawab model cadangan"
```

- Fallback hanya untuk kegagalan kuota, server, timeout, atau jaringan. Error lain (misalnya 400 atau 404) tidak dialihkan dan tampil sebagai error seperti biasa.
- Cadangan otomatis untuk chat tutor dan terjemahan teks pendek (jalur Gemini di halaman Terjemah); Dokumen teks hanya setelah persetujuan pengguna; mesin lokal tidak.
- Kalau Groq juga gagal, pesan error dari Gemini yang ditampilkan.

Detail privasi ada di bagian "Model cadangan dan privasi" di bawah.

Gemini adalah model utama. Kalau Gemini gagal (HTTP 429, gangguan server 5xx, timeout, atau gangguan jaringan), chat tutor dan terjemahan teks pendek (jalur Gemini di halaman Terjemah) otomatis dialihkan ke Groq (`openai/gpt-oss-120b`) supaya kamu tetap bisa berlatih. Balasan dari model cadangan diberi label kecil "Dijawab model cadangan" (chat), "Diterjemahkan model cadangan" (terjemahan), atau "Diproses model cadangan" (dokumen). Kalau Gemini normal, Groq tidak dipanggil sama sekali. Cadangan ini opsional: tanpa `GROQ_API_KEY`, aplikasi hanya memakai Gemini.

## Mulai cepat

**Prasyarat:** Python 3.12 dan tiga kunci API: Google AI Studio (Gemini), Deepgram, dan ElevenLabs. Kunci Groq bersifat opsional, hanya untuk model cadangan. Aplikasi dikembangkan dan diuji di Windows 11.

```powershell
git clone https://github.com/Skywalker0715/fluenta.git
cd fluenta
python -m venv myenv
.\myenv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Isi kunci API di `.env`, lalu jalankan:

```powershell
streamlit run app.py
```

Aplikasi terbuka di `http://localhost:8501`. Pemakaian pertama mengunduh model terjemahan lokal.

## Konfigurasi

Semua nilai dibaca dari `.env`. Tidak ada kunci yang ditulis di dalam kode.

| Variabel | Wajib | Keterangan |
|---|---|---|
| `GEMINI_API_KEY` | Ya | Kunci dari Google AI Studio |
| `GEMINI_MODEL` | Ya | Nama model Flash yang tersedia untuk kuncimu, misalnya `gemini-3.6-flash`. Nama model sering berganti, jadi cek daftar model akunmu |
| `DEEPGRAM_API_KEY` | Ya | Kunci Deepgram |
| `ELEVENLABS_API_KEY` | Ya | Kunci ElevenLabs |
| `ELEVEN_VOICE_ID` | Ya | ID suara kategori `premade`. Akun gratis tidak bisa memakai suara dari voice library lewat API (error 402) |
| `ELEVEN_MODEL_ID` | Tidak | ID model ElevenLabs, default `eleven_turbo_v2_5` |
| `FLUENTA_FORCE_FALLBACK` | Tidak | Sakelar uji: `1` memaksa model cadangan Groq (hanya untuk uji; contoh dalam `.env.example`) |
| `GROQ_API_KEY` | Tidak | Kunci Groq untuk model cadangan. Kosongkan untuk menonaktifkan cadangan |
| `GROQ_MODEL` | Tidak | Model cadangan di Groq, contoh `openai/gpt-oss-120b` |

## Penggunaan

1. **Chat:** ketik pesan, atau klik ikon mikrofon di kolom chat, bicara, lalu diam. Pesan terkirim otomatis.
2. **Bahasa dan level:** pilih di sidebar sebelum mulai berlatih.
3. **Balasan bersuara:** nyalakan atau matikan lewat saklar di sidebar. Matikan untuk menghemat kuota ElevenLabs.
4. **Dokumen:** unggah file, pilih Terjemahkan atau Rangkum, lalu unduh hasilnya sebagai TXT atau DOCX.
5. **Terjemah:** pilih mesin lokal untuk Indonesia ke Inggris, atau Gemini untuk bahasa lain.
6. **Progres:** lihat statistik dan daftar koreksi dari percakapanmu.
7. **Latihan:** buka halaman Latihan untuk latihan ulang koreksi yang jatuh tempo menurut sistem kotak Leitner.

## Struktur proyek

```
fluenta/
├── app.py              Router navigasi dan pengaturan halaman
├── db.py               Akses SQLite
├── views/
│   ├── chat.py         Halaman Chat
│   ├── dokumen.py      Halaman Dokumen
│   ├── terjemah.py     Halaman Terjemah
│   ├── progres.py      Halaman Progres
│   └── latihan.py      Halaman Latihan
├── services/           Logika bisnis (tanpa import Streamlit)
│   ├── llm.py
│   ├── fixparse.py
│   ├── practice.py
│   ├── progress.py
│   ├── stt.py
│   ├── tts.py
│   ├── translate.py
│   └── docs.py
├── assets/             Logo, ikon, dan skrip kirim otomatis
├── docs/               Dokumen perencanaan, arsitektur, dan laporan evaluasi model
├── scripts/            Skrip evaluasi dan tes model cadangan
│   ├── eval_fallback_live.py     Evaluasi fallback langsung
│   ├── eval_groq.py              Evaluasi model cadangan Groq
│   ├── test_fallback_offline.py  Uji fallback offline
│   ├── test_translate_fallback_offline.py  Uji fallback terjemah offline
│   └── test_docs_fallback_offline.py  Uji fallback dokumen offline
├── .streamlit/         Konfigurasi Streamlit
├── .env.example        Contoh konfigurasi
├── .gitignore          Aturan abaikan berkas (termasuk `.env`)
├── LICENSE             Lisensi Apache 2.0
├── NOTICE              Pernyataan hak cipta
└── requirements.txt
```

Folder `data/` dibuat otomatis saat aplikasi pertama dijalankan dan tidak ikut repositori.

## Pengembangan dan tes

Tes offline tidak memanggil API luar. Jalankan dari root repositori:

- `python -m scripts.test_fallback_offline` — uji logika fallback chat (Gemini sukses, 429, 5xx, timeout, error 400 tidak dialihkan, GROQ_API_KEY kosong).
- `python -m scripts.test_translate_fallback_offline` — uji logika fallback terjemah (kasus serupa, serta generate_text lama tidak pernah memanggil Groq).
- `python -m scripts.test_docs_fallback_offline` — uji fallback dokumen (batas 10.000 karakter, pembagian bagian, jeda 3 detik, proses asli tidak memanggil Groq).

Uji paksa model cadangan:

- Isi `FLUENTA_FORCE_FALLBACK=1` di `.env` (contoh tertulis dalam komentar `.env.example`). Dengan sakelar ini, Groq dipakai meski Gemini berhasil. Untuk halaman Dokumen, paksa cadangan hanya berlaku untuk dokumen teks, bukan gambar atau PDF.
- Kembalikan nilai ke `0` atau hapus barisnya setelah selesai uji.

Peringatan: `scripts.eval_fallback_live.py` dan `scripts.eval_groq.py` memanggil API sungguhan (Groq) dan memakai kuota paket Anda. Jalankan hanya saat perlu dan pastikan kuota mencukupi.

## Batasan yang diketahui

- **Kuota gratis terbatas.** Gemini memiliki batas permintaan, dan ElevenLabs sekitar 10.000 karakter per bulan. Pada tier gratis, Google dapat memakai isi percakapan untuk meningkatkan produknya, jadi jangan kirim data pribadi.
- **Kirim otomatis saat diam** memakai JavaScript yang bergantung pada elemen internal Streamlit, sehingga bisa berhenti bekerja setelah pembaruan Streamlit.
- **Mandarin dan Jepang:** koreksi dan balasan teks sudah diuji, tetapi pengenalan ucapan dan kualitas suara untuk dua bahasa itu belum diverifikasi.
- **Belum ada penilaian pelafalan** (pronunciation scoring).
- Berjalan lokal untuk satu pengguna, tanpa login.
- **Mutu cadangan dokumen:** mutu terjemahan dan rangkuman dokumen lewat model cadangan belum diuji luas.
- **Dokumen non-teks tidak punya cadangan.** File gambar dan PDF diproses langsung oleh Gemini; model cadangan Groq hanya untuk teks (TXT, DOCX, MD).
- **Model cadangan** hanya dipakai saat Gemini kena limit atau gangguan, dan hanya untuk chat tutor dan terjemahan teks pendek (jalur Gemini di halaman Terjemah). Penjelasan koreksinya bisa lebih singkat daripada Gemini. Groq tier gratis juga punya batas sendiri (contoh limit yang dipublikasikan: 1.000 permintaan per hari dan 8.000 token per menit, per organisasi); angka pastinya ada di akun Groq-mu.

## Model cadangan dan privasi

Saat Gemini gagal (misalnya HTTP 429, 5xx, timeout, atau gangguan jaringan), pesan chat tutor dan terjemahan teks pendek (jalur Gemini di halaman Terjemah) dapat dialirkan ke model cadangan Groq (`openai/gpt-oss-120b`) sebagai fallback. Hanya jalur chat tutor dan jalur Gemini di halaman Terjemah yang menggunakan fallback otomatis ini.

Halaman Dokumen juga memiliki model cadangan melalui Groq, tetapi tidak otomatis: hanya untuk dokumen teks maksimal sekitar 10.000 karakter, tidak untuk gambar atau PDF, dan isi dokumen hanya dikirim ke Groq setelah pengguna menyetujui dengan mengklik tombol "Pakai model cadangan". Saat fallback aktif, label kecil "Dijawab model cadangan" (chat), "Diterjemahkan model cadangan" (terjemahan), atau "Diproses model cadangan" (dokumen) ditampilkan di bawah balasan. Artinya, saat cadangan aktif, pesan-mu dikirim ke Groq, bukan ke Google.

Kebijakan data tiap penyedia model berbeda, dan pengguna disarankan untuk membaca ketentuan masing-masing sebelum mengirimkan informasi pribadi.

## Peta jalan

Ide ke depan, bukan komitmen:

- [ ] Penilaian pelafalan
- [x] Latihan ulang dari kesalahan lama
- [ ] Deployment dan dukungan banyak pengguna

## Keamanan

`.env` tidak pernah dikomit (tertera di `.gitignore`). Kunci API yang pernah terpapar harus segera dibuat ulang.

## Lisensi

Dirilis dengan lisensi [Apache 2.0](LICENSE). Hak cipta 2026 Rendy Saputra.

Layanan dan model pihak ketiga yang dipakai (Gemini, Deepgram, ElevenLabs, Helsinki-NLP) memiliki ketentuan masing-masing.