import streamlit as st
from pathlib import Path

import db
from services.docs import process_document, to_docx_bytes

st.title("Dokumen")

state = st.session_state

uploaded = st.file_uploader(
    "Unggah dokumen",
    type=["pdf", "docx", "txt", "md", "png", "jpg", "jpeg", "webp"],
)
task_label = st.radio("Tugas", ["Terjemahkan", "Rangkum"], horizontal=True)
target_language = st.selectbox(
    "Bahasa target", ["Indonesia", "English", "Mandarin", "Japanese"]
)

if uploaded is not None and st.button("Proses"):
    task = "translate" if task_label == "Terjemahkan" else "summarize"
    try:
        with st.spinner("Sedang diproses..."):
            result = process_document(
                uploaded.name,
                uploaded.getvalue(),
                uploaded.type or "",
                task,
                target_language,
            )
    except (RuntimeError, ValueError) as exc:
        st.error(str(exc))
    else:
        state["document_result"] = result
        state["document_name"] = uploaded.name
        db.save_document(uploaded.name, task, result)

result = state.get("document_result")
if result:
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
