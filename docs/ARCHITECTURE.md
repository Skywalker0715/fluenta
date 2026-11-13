# Arsitektur

```
app.py (Streamlit UI)
   |
   +-- views/ (chat.py, dokumen.py, progres.py, terjemah.py)
   |
   +-- services/ (tanpa import streamlit)
   |     stt.py       speech_to_text(audio_bytes, lang="en", content_type="audio/wav") -> str
   |     llm.py       ask_tutor(history, lang="en", level="intermediate", mixed=False) -> str
   |     |            split_correction(reply) -> tuple[str, str | None]
   |     |            generate_text(contents, system_instruction, timeout_ms=30000) -> str
   |     |            speakable(conversation) -> str
   |     |            parse_fix(text) -> dict (re-exported from fixparse)
   |     fixparse.py  TAG_LABELS: dict
   |     |            parse_fix(text: str | None) -> dict
   |     progress.py  get_stats() -> dict
   |     |            recent_corrections(limit: int = 20) -> list[dict]
   |     |            corrections_per_day(days: int = 14) -> list[dict]
   |     |            error_patterns(limit: int = 10) -> list[dict]
   |     practice.py  sync() -> int
   |     |            next_items(limit: int = 5) -> list[dict]
   |     |            grade(answer, corrected) -> str
   |     |            record(message_id, result) -> None
   |     |            stats() -> dict
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

## Format Fix line
Baris koreksi berupa satu baris dengan pemisah ` || `:

`Fix: <kalimat yang diperbaiki> || <penjelasan singkat dalam bahasa Indonesia yang menamai aturan> || <tag>`

Tag harus salah satu dari: `past_tense`, `present_tense`, `future_tense`, `articles`, `prepositions`, `subject_verb_agreement`, `plural_singular`, `word_order`, `word_choice`, `collocation`, `code_mixing`, `other`. Jika tidak ada kesalahan nyata, baris Fix tidak ditambahkan. Teks lama tanpa pemisah ` || ` dianggap tidak terstruktur (`structured=False`, `corrected=None`, `explanation=teks asli`, `tag="other"`).