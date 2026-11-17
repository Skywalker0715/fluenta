import os

import streamlit as st
from pathlib import Path

import db
from services.docs import (
    extract_text,
    process_document,
    process_document_groq,
    to_docx_bytes,
)
from services.llm import _should_fallback_to_groq

st.title("Dokumen")

state = st.session_state

_IMAGE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".webp")

uploaded = st.file_uploader(
    "Unggah dokumen",
    type=["pdf", "docx", "txt", "md", "png", "jpg", "jpeg", "webp"],
)
task_label = st.radio("Tugas", ["Terjemahkan", "Rangkum"], horizontal=True)
target_language = st.selectbox(
    "Bahasa target", ["Indonesia", "English", "Mandarin", "Japanese"]
)

_groq_available = bool(os.getenv("GROQ_API_KEY") and os.getenv("GROQ_MODEL"))
_force_fallback = os.getenv("FLUENTA_FORCE_FALLBACK", "0") == "1"


def _is_binary(filename: str) -> bool:
    return filename.lower().endswith(_IMAGE_EXTENSIONS)


if uploaded is not None and st.button("Proses"):
    task = "translate" if task_label == "Terjemahkan" else "summarize"
    is_binary = _is_binary(uploaded.name)
    if _force_fallback:
        if not _groq_available:
            st.error("GROQ_API_KEY atau GROQ_MODEL belum diisi di .env")
        elif is_binary:
            st.error("Model cadangan hanya untuk dokumen teks, bukan file gambar.")
        else:
            state["document_fallback"] = {
                "text": extract_text(uploaded.name, uploaded.getvalue()),
                "task": task,
                "target_language": target_language,
                "name": uploaded.name,
            }
    else:
        try:
            with st.spinner("Sedang diproses..."):
                result = process_document(
                    uploaded.name,
                    uploaded.getvalue(),
                    uploaded.type or "",
                    task,
                    target_language,
                )
        except ValueError as exc:
            st.error(str(exc))
        except RuntimeError as exc:
            if _should_fallback_to_groq(exc) and _groq_available and not is_binary:
                try:
                    teks = extract_text(uploaded.name, uploaded.getvalue())
                except ValueError as exc2:
                    st.error(str(exc2))
                else:
                    state["document_fallback"] = {
                        "text": teks,
                        "task": task,
                        "target_language": target_language,
                        "name": uploaded.name,
                    }
            else:
                st.error(str(exc))
        except Exception:
            st.error("Gagal memproses dokumen.")
        else:
            state["document_result"] = result
            state["document_name"] = uploaded.name
            state["document_result_from_groq"] = False
            state.pop("document_fallback", None)
            db.save_document(uploaded.name, task, result)

_fallback_warning = (
    "Gemini sedang kena batas atau gangguan. Kamu bisa memakai model cadangan. "
    "Isi dokumen akan dikirim ke Groq (penyedia lain)."
)

fallback = state.get("document_fallback")
if fallback:
    st.warning(_fallback_warning)
    if st.button("Pakai model cadangan"):
        try:
            with st.spinner("Sedang diproses dengan model cadangan..."):
                result = process_document_groq(
                    fallback["text"], fallback["task"], fallback["target_language"]
                )
            state["document_result"] = result
            state["document_name"] = fallback["name"]
            state["document_result_from_groq"] = True
            state.pop("document_fallback", None)
            db.save_document(fallback["name"], fallback["task"], result)
        except (RuntimeError, ValueError) as exc:
            st.error(str(exc))

result = state.get("document_result")
if result:
    if state.get("document_result_from_groq"):
        st.caption("Diproses model cadangan")
    st.write(result)
    nama = Path(state.get("document_name") or "dokumen").stem
    st.download_button(
        "Unduh TXT",
        data=result.encode("utf-8"),
        file_name=nama + ".txt",
        mime="text/plain",
    )
    st.download_button(
        "Unduh DOCX",
        data=to_docx_bytes(nama, result),
        file_name=nama + ".docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
