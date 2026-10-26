# Arsitektur

```
app.py (Streamlit UI)
   |
   +-- services/ (tanpa import streamlit)
   |     stt.py       speech_to_text(audio_bytes, lang="en", content_type="audio/wav") -> str
   |     llm.py       ask_tutor(history, lang="en", level="intermediate") -> str
   |     |            split_correction(reply) -> tuple[str, str | None]
   |     |            generate_text(contents, system_instruction, timeout_ms=20000) -> str
   |     |            speakable(conversation) -> str
   |     tts.py       text_to_speech(text, lang="en") -> bytes (mp3)
   |     translate.py translate_id_en(text) -> str
   |     |            translate_text(text, target_language) -> str
   |     docs.py      extract_text(filename, data) -> str
   |     |            process_document(filename, data, mime_type, task, target_language) -> str
   |     |            to_docx_bytes(title, text) -> bytes
   |
   +-- db.py (SQLite) -> data/app.db
```

## Alur suara
mic -> stt -> db.add_message(user) -> llm -> db.add_message(ai)
-> tts (hanya bagian sebelum "Fix:") -> st.audio

## Database
- sessions(id, title, created_at)
- messages(id, session_id, role['user'|'ai'], text, correction, created_at)
- documents(id, filename, task, result_text, created_at)

## Environment (.env)
GEMINI_API_KEY, DEEPGRAM_API_KEY, ELEVENLABS_API_KEY,
GEMINI_MODEL (opsional), ELEVEN_VOICE_ID (opsional)

## Aturan
- UI hanya memanggil services dan db.
- Audio tidak disimpan di DB.
- Format balasan AI: teks balasan, lalu opsional baris "Fix: ...".