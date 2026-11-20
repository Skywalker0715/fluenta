# Audit Suara: Bahasa Inggris, Mandarin, dan Jepang (baca saja)

Dibuat hanya dari bacaan kode `services/stt.py` dan `services/tts.py` (dan pemanggilnya di `views/chat.py`).
Tidak ada kode yang dijalankan, tidak ada nilai variabel lingkungan (`.env`) yang dibuka, dan tidak ada permintaan ke API Deepgram atau ElevenLabs.

## 1. STT — Deepgram (`services/stt.py`)

| Item | Detail dari kode |
|---|---|
| Model | `nova-2` (dikodekan secara konstan, `services/stt.py:15`) |
| Parameter bahasa | Dikirim melalui query parameter `language`, diisi dari argumen `lang` pemanggil (`speech_to_text(audio_bytes, lang="en", content_type="audio/wav")`). Bukan hardcode per bahasa. |
| Parameter lain | `smart_format=true` (`services/stt.py:15`) |
| Pemanggilan dari UI | `views/chat.py:121`: `speech_to_text(audio.getvalue(), content_type="audio/wav", lang=lang_code)`, di mana `lang_code` adalah `"en"`, `"zh"`, atau `"ja"` sesuai pilihan sidebar (`views/chat.py:109`). |

Tidak dapat dipastikan dari kode:
- Apakah model Deepgram `nova-2` mendukung transkripsi untuk Mandarin (`zh`) dan Jepang (`ja`), dan seberapa akurat hasilnya untuk ketiga bahasa.
- Nilai sebenarnya `DEEPGRAM_API_KEY` (disimpan di `.env`, tidak dibaca dalam audit ini).

## 2. TTS — ElevenLabs (`services/tts.py`)

| Item | Detail dari kode |
|---|---|
| Model | `ELEVEN_MODEL_ID` dari `.env`, default `eleven_turbo_v2_5` (`services/tts.py:10`). Satu model untuk semua bahasa. |
| Voice id | `ELEVEN_VOICE_ID` dari `.env` (wajib diisi, tidak ada default, `services/tts.py:9`). Satu voice id untuk semua bahasa. |
| Parameter `lang` | Diterima fungsi `text_to_speech(text, lang="en")` (`services/tts.py:13`) tetapi TIDAK digunakan dalam payload ke ElevenLabs (hanya `text`, `model_id`, `voice_settings`, `services/tts.py:20`). |
| Pemanggilan dari UI | `views/chat.py:99`: `text_to_speech(speakable(conversation))` — argumen `lang` tidak disertakan, sehingga default `"en"` digunakan (namun parameter ini diabaikan oleh fungsi TTS anyway). |

Tidak dapat dipastikan dari kode:
- Apakah model/default voice ElevenLabs menghasilkan ucapan yang natural untuk Mandarin dan Jepang.
- Nilai sebenarnya `ELEVENLABS_API_KEY`, `ELEVEN_VOICE_ID`, dan `ELEVEN_MODEL_ID` (disimpan di `.env`, tidak dibaca).
- Apakah audio berhasil diputar di antarmuka Streamlit (`st.audio` di `views/chat.py:179`).

## 3. Teks yang dibacaan (Pinyin / Romaji / Arti)

Alur suara di `views/chat.py:95-99`:
1. `split_correction(reply)` (`services/llm.py:332`) memisahkan balasan AI menjadi `conversation` (teks sebelum baris `Fix:`) dan `correction` (baris `Fix:`). Hanya `conversation` yang disimpan dan dikirim ke TTS.
2. `text_to_speech(speakable(conversation))` dipanggil.

`speakable` (`services/llm.py:447`) memindai baris-baris percakapan; pada baris pertama yang diawali `Pinyin:`, `Romaji:`, atau `Arti:`, ia memotong teks di titik tersebut dan mengembalikan hanya bagian sebelumnya. Artinya:

- Baris `Pinyin:` (Mandarin), `Romaji:` (Jepang), dan `Arti:` (Mandarin dan Jepang) TIDAK dibacakan oleh TTS.
- Baris `Fix:` sudah tidak ada di `conversation` pada saat pemanggilan TTS, jadi juga tidak dibacakan.
- Hanya teks balasan utama (dalam bahasa target) yang dikirim ke ElevenLabs.

Tidak dapat dipastikan dari kode:
- Apakah ucapan ElevenLabs untuk teks Mandarin dan Jepang dipahami dengan baik oleh pengguna.
- Perilaku runtime STT/TTS (jaringan, kuota API, respons error, latensi).

## Tabel ringkasan

| Komponen | Bahasa | Model / ID | Parameter bahasa | Per bahasa? |
|---|---|---|---|---|
| STT Deepgram | en, zh, ja | `nova-2` (kode) | `language={lang}` dikirim sesuai argumen pemanggil | Parameter dikirim, tapi dukungan Deepgram untuk zh/ja tidak diketahui dari kode |
| TTS ElevenLabs (model) | en, zh, ja | `ELEVEN_MODEL_ID` (default `eleven_turbo_v2_5`) | Tidak dikirim (argumen `lang` diabaikan) | Tidak; satu model untuk semua bahasa |
| TTS ElevenLabs (voice) | en, zh, ja | `ELEVEN_VOICE_ID` (dari `.env`) | — | Tidak; satu voice id untuk semua bahasa |

## Hal yang tidak dapat dipastikan dari kode

- Nilai asli `DEEPGRAM_API_KEY`, `ELEVENLABS_API_KEY`, `ELEVEN_VOICE_ID`, `ELEVEN_MODEL_ID` (disimpan di `.env`; audit tidak membuka file tersebut).
- Apakah Deepgram `nova-2` mendukung bahasa `zh` dan `ja`.
- Kualitas ucapan ElevenLabs untuk teks Mandarin dan Jepang.
- Apakah fitur suara berfungsi pada runtime (koneksi, kuota, respons API, pemutaran audio di Streamlit).