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
| E1 | en | Yesterday I go to the market. | groq | 32.86 | benar | - | ada, tag valid (past_tense) | - | - | - |
| E8 | en | asdf obama purple tomorrow | groq | 1.42 | benar | - | tidak ada | - | - | - |
| Z3 | zh | 我去学校昨天。 | groq | 1.90 | benar | benar | ada, tag valid (word_order) | pypinyin: cocok (pustaka='wǒmíngbáilezuótiānnǐqùxuéxiàolemanǐjīntiānyǒushénmejìhuà' norma_pustaka='wǒmíngbáilezuótiānnǐqùxuéxiàolemanǐjīntiānyǒushénmejìhuà' norma_llm='wǒmíngbáilezuótiānnǐqùxuéxiàolemanǐjīntiānyǒushénmejìhuà') | tidak | tidak |
| J3 | ja | 私は学校を行きます。 | groq | 3.69 | benar | benar | ada, tag valid (prepositions) | cutlet: beda (pustaka='Hai tadashii bun wa watakushi wa gakkou e ikimasu desu Nippon e iku yotei wa arimasu ka' norma_pustaka='haitadashiibunwawatakushiwagakkoueikimasudesunipponeikuyoteiwaarimasuka' norma_llm='haitadashiibunwawatashiwagakkoueikimasudesunihoneikuyoteiwaarimasuka') | tidak | tidak |
| J6 | ja | りんご パソコン 昨日 赤い ね | groq | 2.11 | benar | benar | tidak ada | cutlet: cocok (pustaka='Sumimasen imi ga yoku wakarimasendeshita mou sukoshi kuwashiku oshiete kuremasu ka' norma_pustaka='sumimasenimigayokuwakarimasendeshitamousukoshikuwashikuoshietekuremasuka' norma_llm='sumimasenimigayokuwakarimasendeshitamousukoshikuwashikuoshietekuremasuka') | tidak | - |

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
- Pinyin/Romaji vs pustaka: cocok 1, beda nada saja 0, beda 0, tidak dapat dihitung 0.
- Aksara target setelah Arti: 0 kasus.
- Penjelasan Fix bukan Indonesia: 0 kasus.

## Detail per Kasus

### E1 — en (fix)

Input: Yesterday I go to the market.

Provider: groq | Latensi: 32.86 detik

Jawaban Lengkap LLM:
```
I see. You went to the market yesterday. What did you buy?  
Fix: Yesterday I went to the market. || Kata kerja harus dalam bentuk past tense 'went' karena menyatakan kejadian yang sudah berlalu. || past_tense
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

Provider: groq | Latensi: 1.42 detik

Jawaban Lengkap LLM:
```
I’m not sure I understand. Could you tell me more?
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

Provider: groq | Latensi: 1.90 detik

Jawaban Lengkap LLM:
```
我明白了。昨天你去学校了吗？你今天有什么计划？

Pinyin: Wǒ míngbái le. Zuótiān nǐ qù xuéxiào le ma? Nǐ jīntiān yǒu shénme jìhuà?
Arti: Saya mengerti. Kemarin kamu pergi ke sekolah? Apa rencanamu hari ini?
Fix: 我昨天去学校。 || Keterangan waktu 昨天 diletakkan sebelum kata kerja. || word_order
```

Hasil pustaka:
- pypinyin: cocok (pustaka='wǒmíngbáilezuótiānnǐqùxuéxiàolemanǐjīntiānyǒushénmejìhuà' norma_pustaka='wǒmíngbáilezuótiānnǐqùxuéxiàolemanǐjīntiānyǒushénmejìhuà' norma_llm='wǒmíngbáilezuótiānnǐqùxuéxiàolemanǐjīntiānyǒushénmejìhuà')

Target setelah Arti: tidak
Penjelasan Fix bukan Indonesia: tidak

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J3 — ja (fix)

Input: 私は学校を行きます。

Provider: groq | Latensi: 3.69 detik

Jawaban Lengkap LLM:
```
はい、正しい文は「私は学校へ行きます」です。日本へ行く予定はありますか？  
Romaji: Hai, tadashii bun wa "Watashi wa gakkou e ikimasu" desu. Nihon e iku yotei wa arimasu ka?  
Arti: Ya, kalimat yang benar adalah "Saya pergi ke sekolah". Apakah Anda punya rencana pergi ke Jepang?  
Fix: 私は学校へ行きます。 || Gunakan partikel へ atau に untuk tujuan, bukan を. || prepositions
```

Hasil pustaka:
- cutlet: beda (pustaka='Hai tadashii bun wa watakushi wa gakkou e ikimasu desu Nippon e iku yotei wa arimasu ka' norma_pustaka='haitadashiibunwawatakushiwagakkoueikimasudesunipponeikuyoteiwaarimasuka' norma_llm='haitadashiibunwawatashiwagakkoueikimasudesunihoneikuyoteiwaarimasuka')

Target setelah Arti: tidak
Penjelasan Fix bukan Indonesia: tidak

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J6 — ja (ngawur)

Input: りんご パソコン 昨日 赤い ね

Provider: groq | Latensi: 2.11 detik

Jawaban Lengkap LLM:
```
すみません、意味がよく分かりませんでした。もう少し詳しく教えてくれますか？

Romaji: Sumimasen, imi ga yoku wakarimasen deshita. Mou sukoshi kuwashiku oshiete kuremasu ka?  
Arti: Maaf, saya tidak mengerti maksudnya. Bisakah Anda menjelaskan lebih detail?
```

Hasil pustaka:
- cutlet: cocok (pustaka='Sumimasen imi ga yoku wakarimasendeshita mou sukoshi kuwashiku oshiete kuremasu ka' norma_pustaka='sumimasenimigayokuwakarimasendeshitamousukoshikuwashikuoshietekuremasuka' norma_llm='sumimasenimigayokuwakarimasendeshitamousukoshikuwashikuoshietekuremasuka')

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
