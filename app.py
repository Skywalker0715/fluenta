import streamlit as st

import db

st.set_page_config(page_title="Fluenta", page_icon="assets/icon.png")
db.init_db()

st.logo("assets/logo.png", icon_image="assets/icon.png", size="large")

pages = [
    st.Page("views/chat.py", title="Chat", icon=":material/chat:", default=True),
    st.Page("views/dokumen.py", title="Dokumen", icon=":material/description:"),
    st.Page("views/terjemah.py", title="Terjemah", icon=":material/translate:"),
]

st.navigation(pages).run()