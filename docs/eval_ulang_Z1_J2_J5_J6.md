# Evaluasi Live: Bahasa Inggris, Mandarin, dan Jepang

Panggilan ke `services.llm.ask_tutor_ex` dengan `level='intermediate'` dan history satu pesan user per kasus.
Maksimal 20 panggilan, jeda 5.0 detik, timeout bawaan layanan.
Hanya kasus yang dijalankan: J2, J5, J6, Z1.
Pemeriksaan otomatis (a) sampai (g) bersifat informasi pembantu, bukan penentu satu-satunya kualitas.
Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本schaft dibaca "Nippon go"), jadi "beda" bukan otomatis berarti kesalahan LLM.
Arti dan benarnya koreksi tidak dinilai secara otomatis.
Laporan ini tidak mengandung kunci API.

## Ringkasan per Kasus

| ID | Bahasa | Input | Provider | Latensi (s) | (a) Bahasa balasan | (b) Pinyin/Romaji + Arti | (c) Fix vs harapan | (d) Pinyin/Romaji vs pustaka | (e) Target setelah Arti: | (f) Penjelasan Fix ada Han/kana |
|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | zh | 你好，我叫Roy，我想学中文。 | groq | 14.55 | benar | benar | tidak ada (sesuai harapan) | pypinyin: pustaka tidak terpasang | tidak | - |
| J2 | ja | 今日はいい天気ですね。 | groq | 2.23 | benar | benar | tidak ada (sesuai harapan) | cutlet: cocok (pustaka='Hai kyou wa hontou ni ii tenki desu doko ka de sanpo shitai desu ka' norma_pustaka='haikyouwahontouniiitenkidesudokokadesanposhitaidesuka' norma_llm='haikyouwahontouniiitenkidesudokokadesanposhitaidesuka') | tidak | - |
| J5 | ja | 昨日、友達と映画を見ます。 | groq | 3.53 | benar | benar | ada, tag valid (past_tense) | cutlet: cocok (pustaka='Kinou wa tomodachi to eiga wo mimashita ka donna eiga deshita ka' norma_pustaka='kinouwatomodachitoeigaomimashitakadonnaeigadeshitaka' norma_llm='kinouwatomodachitoeigaomimashitakadonnaeigadeshitaka') | ya | ya |
| J6 | ja | りんご パソコン 昨日 赤い ね | groq | 2.97 | benar | benar | tidak ada | cutlet: beda (pustaka='Kinou akai ringo ga personal computer no ue ni arimashita ka sore wa hontou desu ka dou omoimasu ka' norma_pustaka='kinouakairingogapersonalcomputernoueniarimashitakasorewahontoudesukadouomoimasuka' norma_llm='kinouakairingogapasokonnoueniarimashitakasorewahontoudesukadouomoimasuka') | tidak | - |

## Statistik per Bahasa
### EN (0 kasus)
- Fix sesuai harapan: 0 dari 0 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: tidak berlaku (bukan bahasa target pustaka).

### ZH (1 kasus)
- Fix sesuai harapan: 1 dari 1 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: cocok 0, beda nada saja 0, beda 0, tidak dapat dihitung 1.
- Aksara target setelah Arti: 0 kasus.
- Penjelasan Fix mengandung Han/kana: 0 kasus.

### JA (3 kasus)
- Fix sesuai harapan: 2 dari 2 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: cocok 2, beda nada saja 0, beda 0, tidak dapat dihitung 0.
- Aksara target setelah Arti: 1 kasus.
- Penjelasan Fix mengandung Han/kana: 1 kasus.

## Detail per Kasus

### Z1 — zh (nofix)

Input: 你好，我叫Roy，我想学中文。

Provider: groq | Latensi: 14.55 detik

Jawaban Lengkap LLM:
```
很高兴认识你，Roy。我们可以一起练习中文。你想先学习什么？  
Pinyin: Hěn gāoxìng rènshi nǐ, Roy. Wǒmen kěyǐ yìqǐ liànxí zhōngwén. Nǐ xiǎng xiān xuéxí shénme?  
Arti: Senang bertemu denganmu, Roy. Kita bisa berlatih bahasa Mandarin bersama. Kamu ingin belajar apa dulu?
```

Hasil pustaka:
- pypinyin: pustaka tidak terpasang

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J2 — ja (nofix)

Input: 今日はいい天気ですね。

Provider: groq | Latensi: 2.23 detik

Jawaban Lengkap LLM:
```
はい、今日は本当にいい天気です。どこかで散歩したいですか？

Romaji: Hai, kyou wa hontou ni ii tenki desu. Dokoka de sanpo shitai desu ka?
Arti: Ya, hari ini cuacanya sangat bagus. Apakah kamu ingin jalan‑jalan di mana saja?
```

Hasil pustaka:
- cutlet: cocok (pustaka='Hai kyou wa hontou ni ii tenki desu doko ka de sanpo shitai desu ka' norma_pustaka='haikyouwahontouniiitenkidesudokokadesanposhitaidesuka' norma_llm='haikyouwahontouniiitenkidesudokokadesanposhitaidesuka')

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J5 — ja (fix)

Input: 昨日、友達と映画を見ます。

Provider: groq | Latensi: 3.53 detik

Jawaban Lengkap LLM:
```
昨日は友達と映画を見ましたか？どんな映画でしたか？

Romaji: Kinō wa tomodachi to eiga o mimashita ka? Donna eiga deshita ka?
Arti: Kemarin kamu menonton film dengan teman? Filmnya genre apa?
Fix: 昨日、友達と映画を見ました。 || Kalimat harus memakai bentuk lampau karena menyatakan kejadian di masa lalu, gunakan 見ました bukan 見ます. || past_tense
```

Hasil pustaka:
- cutlet: cocok (pustaka='Kinou wa tomodachi to eiga wo mimashita ka donna eiga deshita ka' norma_pustaka='kinouwatomodachitoeigaomimashitakadonnaeigadeshitaka' norma_llm='kinouwatomodachitoeigaomimashitakadonnaeigadeshitaka')

Target setelah Arti: ya
Penjelasan Fix mengandung Han/kana: ya

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J6 — ja (ngawur)

Input: りんご パソコン 昨日 赤い ね

Provider: groq | Latensi: 2.97 detik

Jawaban Lengkap LLM:
```
昨日、赤いりんごがパソコンの上にありましたか？それは本当ですか？どう思いますか？

Romaji: Kinō, akai ringo ga pasokon no ue ni arimashita ka? Sore wa hontō desu ka? Dō omoimasu ka?
Arti: Kemarin, apakah ada apel merah di atas komputer? Benarkah itu? Apa pendapatmu?
```

Hasil pustaka:
- cutlet: beda (pustaka='Kinou akai ringo ga personal computer no ue ni arimashita ka sore wa hontou desu ka dou omoimasu ka' norma_pustaka='kinouakairingogapersonalcomputernoueniarimashitakasorewahontoudesukadouomoimasuka' norma_llm='kinouakairingogapasokonnoueniarimashitakasorewahontoudesukadouomoimasuka')

Target setelah Arti: tidak
Penjelasan Fix mengandung Han/kana: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

## Catatan
- Pemeriksaan otomatis (a) sampai (g) adalah informasi pembantu, bukan penentu satu-satunya kualitas.
- Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本語 menjadi "Nippon go"), jadi "beda" bukan otomatis berarti kesalahan LLM.
- Arti (baris 'Arti:') dan kebenaran koreksi ('Fix:') harus divalidasi secara manual di kolom yang disediakan.
- Jika panggilan gagal (misal kunci API belum diisi atau jaringan mati), provider dan latensi ditulis sebagai gagal, dan kasus berikutnya tetap dipanggil.
- Tidak ada kunci API yang dicetak atau disimpan dalam laporan ini.
