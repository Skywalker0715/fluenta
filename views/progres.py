import streamlit as st

import db
from services.progress import corrections_per_day, error_patterns, get_stats, recent_corrections

st.title("Progres belajar")

stats = get_stats()
kolom1, kolom2, kolom3 = st.columns(3)
kolom1.metric("Sesi", stats["sessions"])
kolom2.metric("Pesan kamu", stats["user_messages"])
kolom3.metric("Koreksi", stats["corrections"])

harian = corrections_per_day()
if harian:
    st.bar_chart(harian, x="day", y="count")

polas = error_patterns()
if polas:
    st.subheader("Pola kesalahanmu")
    st.bar_chart(polas, x="label", y="count")
    teratas = polas[0]
    st.write(f"Paling sering: {teratas['label']} ({teratas['count']}x)")
else:
    st.write("Belum ada data pola. Pola muncul dari koreksi baru di halaman Chat.")

items = recent_corrections()
if items:
    for item in items:
        with st.expander(item["original"][:40]):
            st.write("Asli:", item["original"])
            st.write("Koreksi:", item["correction"])
    teks_unduh = "\n\n".join(
        f"Asli: {item['original']}\nKoreksi: {item['correction']}\nTanggal: {item['created_at']}"
        for item in items
    )
    st.download_button(
        "Unduh TXT",
        data=teks_unduh.encode("utf-8"),
        file_name="koreksi.txt",
        mime="text/plain",
    )
else:
    st.write("Belum ada data. Mulai ngobrol di halaman Chat.")
