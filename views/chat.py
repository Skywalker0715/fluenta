import html
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import db
from services.llm import ask_tutor, split_correction, speakable
from services.fixparse import parse_fix, TAG_LABELS
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

CSS_STYLE = """
[data-testid="stChatMessageContent"] {
    padding: 0;
    background: transparent;
}
.chat-bubble {
    padding: 10px 14px;
    border-radius: 12px;
    max-width: 75%;
    line-height: 1.5;
    font-size: 0.95rem;
}
.chat-bubble.user {
    background: #6366f1;
    color: #fff;
    margin-inline-start: auto;
}
.chat-bubble.assistant {
    background: rgba(128, 128, 128, 0.15);
    color: inherit;
    margin-inline-end: auto;
}
.correction {
    margin-top: 8px;
    padding: 8px 12px;
    border-left: 3px solid #6366f1;
    background: rgba(99, 102, 241, 0.10);
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    color: inherit;
}
.correction-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 4px;
    display: block;
}
"""
st.markdown(f"<style>{CSS_STYLE}</style>", unsafe_allow_html=True)

state = st.session_state
state.setdefault("session_id", None)
state.setdefault("reply_audio", None)


def open_session(session_id: int | None) -> None:
    state.session_id = session_id
    state.reply_audio = None


def _truncate_judul(title: str | None, panjang: int = 28) -> str:
    teks = title or "Chat"
    if len(teks) > panjang:
        return teks[:panjang] + "..."
    return teks


def handle_user_message(text: str, speak: bool) -> str | None:
    if state.session_id is None:
        state.session_id = db.create_session(title=text[:40])
    db.add_message(state.session_id, "user", text)
    state.reply_audio = None
    try:
        reply = ask_tutor(db.get_messages(state.session_id), lang=lang_code, level=level_belajar, mixed=campur)
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
    campur = st.toggle("Mode ngomong campur", False)
    st.caption("Paling akurat dengan ketikan.")

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
        if col_open.button(_truncate_judul(session["title"]), key=f"s{session['id']}",
                           use_container_width=True):
            open_session(session["id"])
        if col_delete.button("x", key=f"d{session['id']}"):
            db.delete_session(session["id"])
            if state.session_id == session["id"]:
                open_session(None)
            st.rerun()

messages = db.get_messages(state.session_id) if state.session_id else []
if not messages:
    st.write("Halo, ayo latihan bahasa hari ini")
    kolom_saran = st.columns(3)
    for kolom, teks_saran in zip(
        kolom_saran,
        ["Perkenalkan dirimu", "Latihan past tense", "Ceritakan harimu"],
    ):
        if kolom.button(teks_saran, use_container_width=True):
            error = handle_user_message(teks_saran, speak)
else:
    for message in messages:
        role = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(role):
            kelas = "chat-bubble user" if role == "user" else "chat-bubble assistant"
            st.markdown(f'<div class="{kelas}">{html.escape(message["text"])}</div>', unsafe_allow_html=True)
            if message.get("correction"):
                hasil = parse_fix(message["correction"])
                if hasil["structured"]:
                    st.markdown("**Koreksi**")
                    st.write(f"**{hasil['corrected']}**")
                    st.caption(hasil["explanation"])
                    st.caption(f"Tag: {TAG_LABELS[hasil['tag']]}")
                else:
                    st.markdown(
                        '<div class="correction">'
                        '<span class="correction-label">Koreksi</span>'
                        f"{html.escape(message['correction'])}"
                        "</div>",
                        unsafe_allow_html=True,
                    )

if error:
    st.error(error)
if state.reply_audio:
    st.audio(state.reply_audio, format="audio/mp3", autoplay=True)
