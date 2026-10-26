# PRD - Fluenta

## Tujuan
Teman ngobrol bahasa Inggris berbasis AI untuk penutur Indonesia: bicara,
AI membalas dengan suara, dan kesalahan grammar dikoreksi.

## Pengguna
Satu pengguna (pemilik proyek), berjalan lokal di laptop.

## Fitur v1
1. Chat teks dengan tutor AI (Gemini), koreksi grammar ("Fix:") dalam bahasa Indonesia.
2. Chat suara: mic -> Deepgram -> Gemini -> ElevenLabs -> diputar.
3. Terjemahan cepat Indonesia -> Inggris (model lokal).
4. Dokumen: upload PDF/DOCX/TXT, terjemahkan atau rangkum, unduh hasil (TXT/DOCX).
5. Riwayat sesi chat tersimpan di SQLite, daftar sesi di sidebar.

## Kriteria selesai
- Satu giliran suara selesai dalam <= 8 detik.
- Riwayat chat tetap ada setelah aplikasi di-restart.
- Tidak ada API key di kode atau di repo.

## Tidak dikerjakan (dilarang ditambah)
- Penilaian pronunciation
- Streaming real-time dua arah
- Login / multi-user
- Deployment, Docker, CI/CD
- Terjemahan model lokal selain id->en (bahasa lain lewat Gemini)
- Penyimpanan audio di database

## Bahasa
- v1: Inggris, Mandarin, Jepang lewat parameter lang. Kualitas STT/TTS non-Inggris belum diverifikasi.