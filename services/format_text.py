import html
import re

_PENORA = re.compile(r"(\S)\s*(Pinyin:|Romaji:|Arti:)")


def format_bubble(teks: str) -> str:
    """Escape teks untuk HTML, ubah baris baru menjadi <br>, dan sisipkan
    <br> sebelum penanda Pinyin:/Romaji:/Arti: yang didahului teks pada
    baris yang sama agar tidak menyatu dalam satu paragraf."""
    keluar = html.escape(teks)
    keluar = keluar.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    baris = keluar.split("<br>")
    dipisah = [_PENORA.sub(r"\1<br>\2", baris_teks) for baris_teks in baris]
    return "<br>".join(dipisah)
