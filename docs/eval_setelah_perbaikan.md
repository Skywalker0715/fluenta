# Evaluasi Live: Bahasa Inggris, Mandarin, dan Jepang

Panggilan ke `services.llm.ask_tutor_ex` dengan `level='intermediate'` dan history satu pesan user per kasus.
Maksimal 20 panggilan, jeda 5.0 detik, timeout bawaan layanan.
Hanya kasus yang dijalankan: J2, J3, J5, J6, Z1.
Pemeriksaan otomatis (a) sampai (g) bersifat informasi pembantu, bukan penentu satu-satunya kualitas.
Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本schaft dibaca "Nippon go"), jadi "beda" bukan otomatis berarti kesalahan LLM.
Arti dan benarnya koreksi tidak dinilai secara otomatis.
Laporan ini tidak mengandung kunci API.

## Ringkasan per Kasus

| ID | Bahasa | Input | Provider | Latensi (s) | (a) Bahasa balasan | (b) Pinyin/Romaji + Arti | (c) Fix vs harapan | (d) Pinyin/Romaji vs pustaka | (e) Target setelah Arti: | (f) Penjelasan Fix ada Han/kana |
|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | zh | 你好，我叫Roy，我想学中文。 | groq | 32.71 | benar | benar | tidak ada (sesuai harapan) | pypinyin: cannot import name 'pypinyin' from 'pypinyin' (D:\Ngoding dan AI Project\AI Project Mini\Translator\myenv\Lib\site-packages\pypinyin\__init__.py) | tidak | - |
| J2 | ja | 今日はいい天気ですね。 | groq | 2.32 | benar | benar | tidak ada (sesuai harapan) | cutlet: cocok (pustaka='Hai kyou wa totemo ii tenki desu doko ka ni ikitai desu ka' norma_pustaka='haikyouwatotemoiitenkidesudokokaniikitaidesuka' norma_llm='haikyouwatotemoiitenkidesudokokaniikitaidesuka') | tidak | - |
| J3 | ja | 私は学校を行きます。 | groq | 2.48 | benar | benar | ada, tag valid (prepositions) | cutlet: beda (pustaka='Hai ganbatte kudasai tsugi ni nan wo benkyou shitai desu ka' norma_pustaka='haiganbattekudasaitsugininanobenkyoushitaidesuka' norma_llm='haiganbattekudasaitsugininaniobenkyoushitaidesuka') | tidak | ya |
| J5 | ja | 昨日、友達と映画を見ます。 | groq | 2.64 | benar | benar | ada, tag valid (past_tense) | cutlet: cocok (pustaka='Eiga wa tanoshikatta desu ka donna eiga deshita ka' norma_pustaka='eigawatanoshikattadesukadonnaeigadeshitaka' norma_llm='eigawatanoshikattadesukadonnaeigadeshitaka') | tidak | tidak |
| J6 | ja | りんご パソコン 昨日 赤い ね | groq | 3.27 | benar | benar | ada | cutlet: beda (pustaka='Kinou akai personal computer ni tsuite hanashimashita ne iro no iikata wa jouzu desu hoka ni nan wo mimashita ka' norma_pustaka='kinouakaipersonalcomputernitsuitehanashimashitaneironoiikatawajouzudesuhokaninanomimashitaka' norma_llm='kinouakaipasokonnitsuitehanashimashitaneironoiikatawajouzudesuhokaninaniomimashitaka') | tidak | ya |

## Statistik per Bahasa
### EN (0 kasus)
- Fix sesuai harapan: 0 dari 0 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: tidak berlaku (bukan bahasa target pustaka).

### ZH (1 kasus)
- Fix sesuai harapan: 1 dari 1 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: cocok 0, beda nada saja 0, beda 0, tidak dapat dihitung 0.
- Aksara target setelah Arti: 0 kasus.
- Penjelasan Fix mengandung Han/kana: 0 kasus.

### JA (4 kasus)
- Fix sesuai harapan: 3 dari 3 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: cocok 2, beda nada saja 0, beda 0, tidak dapat dihitung 0.
- Aksara target setelah Arti: 0 kasus.
- Penjelasan Fix mengandung Han/kana: 2 kasus.

## Detail per Kasus

### Z1 — zh (nofix)

Input: 你好，我叫Roy，我想学中文。

Provider: groq | Latensi: 32.71 detik

Jawaban Lengkap LLM:
```
很高兴认识你，Roy。我们可以一起练习中文。你想先学习哪些内容？

Pinyin: Hěn gāoxìng rènshi nǐ, Roy. Wǒmen kěyǐ yìqǐ liànxí zhōngwén. Nǐ xiǎng xiān xuéxí nǎxiē nèiróng?
Arti: Senang bertemu denganmu, Roy. Kita bisa berlatih bahasa Mandarin bersama. Kamu ingin belajar apa dulu?
```

Hasil pustaka:
- pypinyin: cannot import name 'pypinyin' from 'pypinyin' (D:\Ngoding dan AI Project\AI Project Mini\Translator\myenv\Lib\site-packages\pypinyin\__init__.py)

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J2 — ja (nofix)

Input: 今日はいい天気ですね。

Provider: groq | Latensi: 2.32 detik

Jawaban Lengkap LLM:
```
はい、今日はとてもいい天気です。どこかに行きたいですか？

Romaji: Hai, kyou wa totemo ii tenki desu. Doko ka ni ikitai desu ka?
Arti: Ya, hari ini cuacanya sangat bagus. Apakah kamu ingin pergi ke suatu tempat?
```

Hasil pustaka:
- cutlet: cocok (pustaka='Hai kyou wa totemo ii tenki desu doko ka ni ikitai desu ka' norma_pustaka='haikyouwatotemoiitenkidesudokokaniikitaidesuka' norma_llm='haikyouwatotemoiitenkidesudokokaniikitaidesuka')

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J3 — ja (fix)

Input: 私は学校を行きます。

Provider: groq | Latensi: 2.48 detik

Jawaban Lengkap LLM:
```
はい、がんばってください。次に何を勉強したいですか？

Romaji: Hai, ganbatte kudasai. Tsugi ni nani o benkyou shitai desu ka?
Arti: Ya, semangat ya. Selanjutnya apa yang ingin kamu pelajari?
Fix: 私は学校へ行きます。 || Tujuan (ke sekolah) menggunakan partikel へ atau に, bukan を. || prepositions
```

Hasil pustaka:
- cutlet: beda (pustaka='Hai ganbatte kudasai tsugi ni nan wo benkyou shitai desu ka' norma_pustaka='haiganbattekudasaitsugininanobenkyoushitaidesuka' norma_llm='haiganbattekudasaitsugininaniobenkyoushitaidesuka')

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: ya

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J5 — ja (fix)

Input: 昨日、友達と映画を見ます。

Provider: groq | Latensi: 2.64 detik

Jawaban Lengkap LLM:
```
映画は楽しかったですか？どんな映画でしたか？
Romaji: Eiga wa tanoshikatta desu ka? Donna eiga deshita ka?
Arti: Apakah filmnya menyenangkan? Film apa itu?
Fix: 昨日、友達と映画を見ました。 || Kata '昨日' menunjukkan waktu lampau, sehingga kata kerja harus dalam bentuk past tense '見ました', bukan '見ます'. || past_tense
```

Hasil pustaka:
- cutlet: cocok (pustaka='Eiga wa tanoshikatta desu ka donna eiga deshita ka' norma_pustaka='eigawatanoshikattadesukadonnaeigadeshitaka' norma_llm='eigawatanoshikattadesukadonnaeigadeshitaka')

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: tidak

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J6 — ja (ngawur)

Input: りんご パソコン 昨日 赤い ね

Provider: groq | Latensi: 3.27 detik

Jawaban Lengkap LLM:
```
昨日、赤いパソコンについて話しましたね。色の言い方は上手です。ほかに何を見ましたか？
Romaji: Kinō, akai pasokon ni tsuite hanashimashita ne. Iro no iikata wa jōzu desu. Hoka ni nani o mimashita ka?
Arti: Kemarin, kita membicarakan tentang komputer merah, ya. Cara menyebut warna sudah bagus. Apa lagi yang kamu lihat?
Fix: 昨日、赤いパソコンがありましたね。 || Subjek dan predikat harus lengkap, gunakan partikel が untuk subjek dan ありました untuk menyatakan keberadaan di masa lalu. || past_tense
```

Hasil pustaka:
- cutlet: beda (pustaka='Kinou akai personal computer ni tsuite hanashimashita ne iro no iikata wa jouzu desu hoka ni nan wo mimashita ka' norma_pustaka='kinouakaipersonalcomputernitsuitehanashimashitaneironoiikatawajouzudesuhokaninanomimashitaka' norma_llm='kinouakaipasokonnitsuitehanashimashitaneironoiikatawajouzudesuhokaninaniomimashitaka')

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: ya

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

## Catatan
- Pemeriksaan otomatis (a) sampai (g) adalah informasi pembantu, bukan penentu satu-satunya kualitas.
- Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本語 menjadi "Nippon go"), jadi "beda" bukan otomatis berarti kesalahan LLM.
- Arti (baris 'Arti:') dan kebenaran koreksi ('Fix:') harus divalidasi secara manual di kolom yang disediakan.
- Jika panggilan gagal (misal kunci API belum diisi atau jaringan mati), provider dan latensi ditulis sebagai gagal, dan kasus berikutnya tetap dipanggil.
- Tidak ada kunci API yang dicetak atau disimpan dalam laporan ini.
