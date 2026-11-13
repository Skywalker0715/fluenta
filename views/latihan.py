import streamlit as st

from services.fixparse import TAG_LABELS
from services.practice import grade, next_items, record, stats, sync

st.title("Latihan dari kesalahanmu")

state = st.session_state
state.setdefault("latihan_item", None)
state.setdefault("latihan_items", None)
state.setdefault("latihan_index", 0)
state.setdefault("latihan_checked", False)

sync()

total = stats()["total"]
jatuh_tempo = stats()["due"]
dikuasai = stats()["mastered"]
kolom1, kolom2, kolom3 = st.columns(3)
kolom1.metric("Total", total)
kolom2.metric("Jatuh tempo", jatuh_tempo)
kolom3.metric("Dikuasai", dikuasai)

if state.latihan_items is None:
    items = next_items()
    state.latihan_items = items
    state.latihan_index = 0
    state.latihan_item = items[0] if items else None

item = state.latihan_item
if item is None:
    st.write("Belum ada soal. Ngobrol di halaman Chat; hanya koreksi baru yang bisa dilatih.")
else:
    st.write("Perbaiki kalimat ini")
    st.write(item["original"])
    jawaban = st.text_input("Jawaban", key="latihan_jawaban")
    if st.button("Periksa"):
        hasil = grade(jawaban, item["corrected"])
        record(item["message_id"], hasil)
        state.latihan_hasil = hasil
        state.latihan_checked = True
        st.rerun()

    if state.latihan_checked:
        st.write(f"Hasil: {state.latihan_hasil}")
        st.write(f"Benar: {item['corrected']}")
        st.caption(item["explanation"])
        st.caption(f"Tag: {TAG_LABELS[item['tag']]}")
        if st.button("Berikutnya"):
            items = state.latihan_items or []
            next_idx = state.latihan_index + 1
            if next_idx < len(items):
                state.latihan_item = items[next_idx]
                state.latihan_index = next_idx
            else:
                state.latihan_item = None
            state.latihan_checked = False
            st.rerun()
