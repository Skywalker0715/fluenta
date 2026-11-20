# Evaluasi Live: Bahasa Inggris, Mandarin, dan Jepang

Panggilan ke `services.llm.ask_tutor_ex` dengan `level='intermediate'` dan history satu pesan user per kasus.
Maksimal 20 panggilan, jeda 5.0 detik, timeout bawaan layanan.
Hanya kasus yang dijalankan: E1, E8, J3, J6, Z3.
Pemeriksaan otomatis (a) sampai (g) bersifat informasi pembantu, bukan penentu satu-satunya kualitas.
Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本schaft dibaca "Nippon go"), jadi "beda" bukan otomatis berarti kesalahan LLM.
Arti dan benarnya koreksi tidak dinilai secara otomatis.
Laporan ini tidak mengandung kunci API.

## Ringkasan per Kasus

| ID | Bahasa | Input | Provider | Latensi (s) | (a) Bahasa balasan | (b) Pinyin/Romaji + Arti | (c) Fix vs harapan | (d) Pinyin/Romaji vs pustaka | (e) Target setelah Arti: | (f) Penjelasan Fix bukan Indonesia |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | en | Yesterday I go to the market. | groq | 34.54 | benar | - | ada, tag valid (past_tense) | - | - | - |
| E8 | en | asdf obama purple tomorrow | groq | 2.05 | benar | - | tidak ada | - | - | - |
| Z3 | zh | 我去学校昨天。 | groq | 2.47 | benar | benar | ada, tag valid (word_order) | pypinyin: cocok (pustaka='wǒzuótiānqùxuéxiàonǐjīntiānqùxuéxiàolema' norma_pustaka='wǒzuótiānqùxuéxiàonǐjīntiānqùxuéxiàolema' norma_llm='wǒzuótiānqùxuéxiàonǐjīntiānqùxuéxiàolema') | tidak | tidak |
| J3 | ja | 私は学校を行きます。 | groq | 2.36 | benar | benar | ada, tag valid (other) | cutlet: beda (pustaka='Ganbatte imasu ne gakkou e iku toki wa tanoshinde kudasai tsugi wa nan wo benkyou shitai desu ka' norma_pustaka='ganbatteimasunegakkoueikutokiwatanoshindekudasaitsugiwananobenkyoushitaidesuka' norma_llm='ganbatteimasunegakkoueikutokiwatanoshindekudasaitsugiwananiobenkyoushitaidesuka') | tidak | tidak |
| J6 | ja | りんご パソコン 昨日 赤い ね | groq | 2.21 | benar | benar | tidak ada | cutlet: beda (pustaka='Konnichiha ikutsu ka no tango wo kakimashita ne korera ni tsuite nan ka shitsumon ga arimasu ka' norma_pustaka='konnichihaikutsukanotangookakimashitanekoreranitsuitenankashitsumongaarimasuka' norma_llm='konnichiwaikutsukanotangookakimashitanekoreranitsuitenanikashitsumongaarimasuka') | tidak | - |

## Statistik per Bahasa
### EN (2 kasus)
- Fix sesuai harapan: 1 dari 1 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: tidak berlaku (bukan bahasa target pustaka).

### ZH (1 kasus)
- Fix sesuai harapan: 1 dari 1 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: cocok 1, beda nada saja 0, beda 0, tidak dapat dihitung 0.
- Aksara target setelah Arti: 0 kasus.
- Penjelasan Fix bukan Indonesia: 0 kasus.

### JA (2 kasus)
- Fix sesuai harapan: 1 dari 1 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: cocok 0, beda nada saja 0, beda 0, tidak dapat dihitung 0.
- Aksara target setelah Arti: 0 kasus.
- Penjelasan Fix bukan Indonesia: 0 kasus.

## Detail per Kasus

### E1 — en (fix)

Input: Yesterday I go to the market.

Provider: groq | Latensi: 34.54 detik

Jawaban Lengkap LLM:
```
Going to the market can be fun. Did you find anything interesting?

Fix: Yesterday I went to the market. || Penjelasan: Karena kata kerja 'go' harus dalam bentuk past tense 'went' untuk menyatakan aksi di masa lalu. || past_tense
```

Hasil pustaka:
- -

Target setelah Arti: -
Penjelasan Fix bukan Indonesia: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E8 — en (ngawur)

Input: asdf obama purple tomorrow

Provider: groq | Latensi: 2.05 detik

Jawaban Lengkap LLM:
```
I’m not sure I understand. Could you please rephrase? What would you like to talk about?
```

Hasil pustaka:
- -

Target setelah Arti: -
Penjelasan Fix bukan Indonesia: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### Z3 — zh (fix)

Input: 我去学校昨天。

Provider: groq | Latensi: 2.47 detik

Jawaban Lengkap LLM:
```
我昨天去学校。你今天去学校了吗？

Pinyin: Wǒ zuótiān qù xuéxiào. Nǐ jīntiān qù xuéxiào le ma?
Arti: Saya pergi ke sekolah kemarin. Apakah kamu pergi ke sekolah hari ini?

Fix: 我昨天去学校。 || Keterangan waktu 昨天 diletakkan sebelum kata kerja. || word_order
```

Hasil pustaka:
- pypinyin: cocok (pustaka='wǒzuótiānqùxuéxiàonǐjīntiānqùxuéxiàolema' norma_pustaka='wǒzuótiānqùxuéxiàonǐjīntiānqùxuéxiàolema' norma_llm='wǒzuótiānqùxuéxiàonǐjīntiānqùxuéxiàolema')

Target setelah Arti: tidak
Penjelasan Fix bukan Indonesia: tidak

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J3 — ja (fix)

Input: 私は学校を行きます。

Provider: groq | Latensi: 2.36 detik

Jawaban Lengkap LLM:
```
がんばっていますね。学校へ行くときは楽しんでください。次は何を勉強したいですか？

Romaji: Ganbatte imasu ne. Gakkou e iku toki wa tanoshinde kudasai. Tsugi wa nani o benkyou shitai desu ka?
Arti: Bagus, semangat ya. Saat pergi ke sekolah, silakan bersenang‑senang. Selanjutnya, apa yang ingin kamu pelajari?

Fix: 私は学校へ行きます。 || Tujuan harus menggunakan partikel へ atau に, bukan を. || prepositions.
```

Hasil pustaka:
- cutlet: beda (pustaka='Ganbatte imasu ne gakkou e iku toki wa tanoshinde kudasai tsugi wa nan wo benkyou shitai desu ka' norma_pustaka='ganbatteimasunegakkoueikutokiwatanoshindekudasaitsugiwananobenkyoushitaidesuka' norma_llm='ganbatteimasunegakkoueikutokiwatanoshindekudasaitsugiwananiobenkyoushitaidesuka')

Target setelah Arti: tidak
Penjelasan Fix bukan Indonesia: tidak

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J6 — ja (ngawur)

Input: りんご パソコン 昨日 赤い ね

Provider: groq | Latensi: 2.21 detik

Jawaban Lengkap LLM:
```
こんにちは。いくつかの単語を書きましたね。これらについて何か質問がありますか？

Romaji: Konnichiwa. Ikutsuka no tango o kakimashita ne. Korera ni tsuite nanika shitsumon ga arimasu ka?
Arti: Halo. Kamu menulis beberapa kata. Apakah ada pertanyaan tentang hal‑hal ini?
```

Hasil pustaka:
- cutlet: beda (pustaka='Konnichiha ikutsu ka no tango wo kakimashita ne korera ni tsuite nan ka shitsumon ga arimasu ka' norma_pustaka='konnichihaikutsukanotangookakimashitanekoreranitsuitenankashitsumongaarimasuka' norma_llm='konnichiwaikutsukanotangookakimashitanekoreranitsuitenanikashitsumongaarimasuka')

Target setelah Arti: tidak
Penjelasan Fix bukan Indonesia: -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

## Catatan
- Pemeriksaan otomatis (a) sampai (g) adalah informasi pembantu, bukan penentu satu-satunya kualitas.
- Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本語 menjadi "Nippon go"), jadi "beda" bukan otomatis berarti kesalahan LLM.
- Arti (baris 'Arti:') dan kebenaran koreksi ('Fix:') harus divalidasi secara manual di kolom yang disediakan.
- Jika panggilan gagal (misal kunci API belum diisi atau jaringan mati), provider dan latensi ditulis sebagai gagal, dan kasus berikutnya tetap dipanggil.
- Tidak ada kunci API yang dicetak atau disimpan dalam laporan ini.
