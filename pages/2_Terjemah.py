import streamlit as st

from services.translate import translate_id_en, translate_text

st.set_page_config(page_title="Fluenta", page_icon="assets/icon.png")

st.title("Terjemah")

text = st.text_area("Teks", height=200)
engine = st.radio(
    "Mesin",
    [
        "Cepat: Indonesia ke Inggris (model lokal)",
        "Gemini: bahasa lain",
    ],
)
target_language = None
if engine == "Gemini: bahasa lain":
    target_language = st.selectbox(
        "Bahasa target", ["Indonesia", "English", "Mandarin", "Japanese"]
    )

if st.button("Terjemahkan"):
    try:
        if engine == "Cepat: Indonesia ke Inggris (model lokal)":
            result = translate_id_en(text)
        else:
            result = translate_text(text, target_language)
    except RuntimeError as exc:
        st.error(str(exc))
    else:
        st.code(result)