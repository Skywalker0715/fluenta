import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.format_text import format_bubble

results = []


def check(nama: str, kondisi: bool, detail: str = "") -> None:
    status = "PASS" if kondisi else "FAIL"
    results.append((nama, status))
    print(f"{status}: {nama}{detail}")


# (a) baris baru tunggal menjadi <br>
check(
    "a) baris baru tunggal -> <br>",
    format_bubble("baris satu\nbaris dua") == "baris satu<br>baris dua",
)

# (b) "ka? Arti: Halo" memisahkan Arti ke baris baru
check(
    "b) 'ka? Arti: Halo' memisahkan Arti ke baris baru",
    format_bubble("ka? Arti: Halo") == "ka?<br>Arti: Halo",
)

# (c) <b> ter-escape, tampil apa adanya
check(
    "c) '<b>halo</b> & \"tes\" ter-escape",
    format_bubble('<b>halo</b> & "tes"')
    == "&lt;b&gt;halo&lt;/b&gt; &amp; &quot;tes&quot;",
)

# (d) teks tanpa penanda tidak berubah
check(
    "d) teks tanpa penanda tidak berubah",
    format_bubble("Halo, apa kabar?") == "Halo, apa kabar?",
)

# penanda di awal baris tidak disisipkan <br> di depannya
check(
    "e) penanda di awal baris tidak dipisah",
    format_bubble("Pinyin: pin\nArti: arti") == "Pinyin: pin<br>Arti: arti",
)

# gabungan Pinyin dan Romaji pada satu baris
check(
    "f) Pinyin dan Romaji dipisah",
    format_bubble("ini Pinyin: pin, Romaji: rm")
    == "ini<br>Pinyin: pin,<br>Romaji: rm",
)

print("\n=== Ringkasan Tes Offline ===")
passed = sum(1 for _, s in results if s == "PASS")
failed = sum(1 for _, s in results if s == "FAIL")
for nama, status in results:
    print(f"  {status}: {nama}")
print(f"\nLulus: {passed}/{len(results)}")
if failed:
    print(f"Gagal: {failed}")
    sys.exit(1)
