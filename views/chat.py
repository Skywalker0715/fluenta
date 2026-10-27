import streamlit as st
import json
from pathlib import Path

import streamlit.components.v1 as components

import db
from services.llm import ask_tutor, split_correction, speakable
from services.stt import speech_to_text
from services.tts import text_to_speech

_AUTO_SEND = Path("assets/auto_send.js").read_text(encoding="utf-8")
components.html(
    "<script>"
    "const s = window.parent.document.createElement('script');"
    f"s.textContent = {json.dumps(_AUTO_SEND)};"
    "window.parent.document.head.appendChild(s);"
    "</script>",
    height=0,
)

state = st.session_state
state.setdefault("session_id", None)
state.setdefault("reply_audio", None)


def open_session(session_id: int | None) -> None:
    state.session_id = session_id
    state.reply_audio = None


def handle_user_message(text: str, speak: bool) -> str | None:
    if state.session_id is None:
        state.session_id = db.create_session(title=text[:40])
    db.add_message(state.session_id, "user", text)
    state.reply_audio = None
    try:
        reply = ask_tutor(db.get_messages(state.session_id), lang=lang_code, level=level_belajar)
    except RuntimeError as exc:
        return str(exc)
    conversation, correction = split_correction(reply)
    db.add_message(state.session_id, "ai", conversation, correction)
    if speak:
        try:
            state.reply_audio = text_to_speech(speakable(conversation))
        except RuntimeError as exc:
            return str(exc)
    return None


with st.sidebar:
    speak = st.toggle("Balasan bersuara", value=True)
    bahasa_belajar = st.selectbox("Bahasa belajar", ["English", "Mandarin", "Japanese"])
    level_belajar = st.select_slider("Level", ["beginner", "intermediate", "advanced"], value="intermediate")
    _KODE_BAHASA = {"English": "en", "Mandarin": "zh", "Japanese": "ja"}
    lang_code = _KODE_BAHASA[bahasa_belajar]

prompt = st.chat_input("Tulis atau rekam suaramu...", accept_audio=True)
error = None
if prompt:
    text = (prompt.text or "").strip()
    audio = getattr(prompt, "audio", None)
    if not text and audio:
        try:
            text = speech_to_text(audio.getvalue(), content_type="audio/wav", lang=lang_code)
        except RuntimeError as exc:
            error = str(exc)
        else:
            if not text:
                error = "Suara tidak terdengar, coba lagi."
    if text:
        error = handle_user_message(text, speak)

with st.sidebar:
    if st.button("Chat baru", use_container_width=True):
        open_session(None)
    for session in db.list_sessions()[:15]:
        col_open, col_delete = st.columns([5, 1])
        if col_open.button(session["title"] or "Chat", key=f"s{session['id']}",
                           use_container_width=True):
            open_session(session["id"])
        if col_delete.button("x", key=f"d{session['id']}"):
            db.delete_session(session["id"])
            if state.session_id == session["id"]:
                open_session(None)
            st.rerun()

messages = db.get_messages(state.session_id) if state.session_id else []
for message in messages:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.write(message["text"])
        if message.get("correction"):
            st.info(message["correction"])

if error:
    st.error(error)
if state.reply_audio:
    st.audio(state.reply_audio, format="audio/mp3", autoplay=True)
