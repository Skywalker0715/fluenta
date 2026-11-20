# Evaluasi Live: Bahasa Inggris, Mandarin, dan Jepang

Panggilan ke `services.llm.ask_tutor_ex` dengan `level='intermediate'` dan history satu pesan user per kasus.
Maksimal 20 panggilan, jeda 3 detik, timeout bawaan layanan.
Pemeriksaan otomatis (a) sampai (d) bersifat informasi, bukan penentu satu-satunya.
Arti dan benarnya koreksi tidak dinilai secara otomatis.
Laporan ini tidak mengandung kunci API.

## Ringkasan per Kasus

| ID | Bahasa | Input | Provider | Latensi (s) | (a) Bahasa balasan | (b) Pinyin/Romaji + Arti | (c) Fix vs harapan | (d) Pinyin/Romaji vs pustaka |
|---|---|---|---|---|---|---|---|---|
| E1 | en | Yesterday I go to the market. | gemini | 13.68 | benar | - | ada, tapi gagal parse atau tag tidak valid | - |
| E2 | en | I have a cat and two dog. | gemini | 13.39 | benar | - | ada, tapi gagal parse atau tag tidak valid | - |
| E3 | en | She don't like coffee. | gemini | 9.27 | benar | - | ada, tapi gagal parse atau tag tidak valid | - |
| E4 | en | I am agree with you. | gemini | 5.21 | benar | - | ada, tapi gagal parse atau tag tidak valid | - |
| E5 | en | I went to school yesterday. | gemini | 17.00 | benar | - | tidak ada (sesuai harapan) | - |
| E6 | en | Can you recommend a good restaurant near here? | gemini | 18.26 | benar | - | tidak ada (sesuai harapan) | - |
| E7 | en | aku mau order coffee, tapi gimana ya bilangnya? | gemini | 21.66 | benar | - | ada, tapi gagal parse atau tag tidak valid | - |
| E8 | en | asdf obama purple tomorrow | gemini | 20.36 | benar | - | tidak ada | - |
| Z1 | zh | 你好，我叫Roy，我想学中文。 | gemini | 46.61 | benar | benar | tidak ada (sesuai harapan) | pypinyin: pustaka tidak terpasang |
| Z2 | zh | Wo xihuan chi fan. | gemini | 16.40 | benar | benar | tidak ada (sesuai harapan) | pypinyin: pustaka tidak terpasang |
| Z3 | zh | 我去学校昨天。 | gemini | 48.39 | benar | benar | ada, tapi gagal parse atau tag tidak valid | pypinyin: pustaka tidak terpasang |
| Z4 | zh | 我有三个书。 | gemini | 53.65 | benar | benar | ada, tapi gagal parse atau tag tidak valid | pypinyin: pustaka tidak terpasang |
| Z5 | zh | 他是很高。 | gemini | 7.63 | benar | benar | ada, tapi gagal parse atau tag tidak valid | pypinyin: pustaka tidak terpasang |
| Z6 | zh | 苹果 电脑 昨天 红色 啊 | gagal | - | salah | salah (Pinyin=False, Arti=False) | tidak ada | pypinyin: pustaka tidak terpasang |
| J1 | ja | Watashi wa gakusei desu. | gagal | - | salah | salah (Romaji=False, Arti=False) | tidak ada (sesuai harapan) | cutlet: tidak dapat dihitung |
| J2 | ja | 今日はいい天気ですね。 | gagal | - | salah | salah (Romaji=False, Arti=False) | tidak ada (sesuai harapan) | cutlet: tidak dapat dihitung |
| J3 | ja | 私は学校を行きます。 | gagal | - | salah | salah (Romaji=False, Arti=False) | tidak ada (harapan: ada) | cutlet: tidak dapat dihitung |
| J4 | ja | 私は日本語を話すができます。 | gagal | - | salah | salah (Romaji=False, Arti=False) | tidak ada (harapan: ada) | cutlet: tidak dapat dihitung |
| J5 | ja | 昨日、友達と映画を見ます。 | gagal | - | salah | salah (Romaji=False, Arti=False) | tidak ada (harapan: ada) | cutlet: tidak dapat dihitung |
| J6 | ja | りんご パソコン 昨日 赤い ね | gemini | 14.86 | benar | benar | tidak ada | cutlet: beda |

## Statistik per Bahasa
### EN (8 kasus)
- Fix sesuai harapan: 2 dari 2 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: tidak berlaku (bukan bahasa target pustaka).

### ZH (6 kasus)
- Fix sesuai harapan: 2 dari 2 kasus (fix/nofix).
- Fix tidak sesuai harapan: 0 kasus.
- Pinyin/Romaji vs pustaka: cocok 0, beda nada saja 0, beda 0, tidak dapat dihitung 6.

### JA (6 kasus)
- Fix sesuai harapan: 2 dari 5 kasus (fix/nofix).
- Fix tidak sesuai harapan: 3 kasus.
- Pinyin/Romaji vs pustaka: cocok 0, beda nada saja 0, beda 1, tidak dapat dihitung 5.

## Detail per Kasus

### E1 — en (fix)

Input: Yesterday I go to the market.

Provider: gemini | Latensi: 13.68 detik

Jawaban Lengkap LLM:
```
That sounds like a busy day! What kind of things did you buy at the market?

Fix: Yesterday I went to the market. || Gunakan "went" karena kejadian tersebut terjadi di masa lalu (yesterday). || past_tense
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E2 — en (fix)

Input: I have a cat and two dog.

Provider: gemini | Latensi: 13.39 detik

Jawaban Lengkap LLM:
```
That sounds like a fun house with so many pets! What are their names?

Fix: I have a cat and two dogs. || Gunakan kata benda jamak (dogs) setelah angka lebih dari satu (two). || plural_singular
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E3 — en (fix)

Input: She don't like coffee.

Provider: gemini | Latensi: 9.27 detik

Jawaban Lengkap LLM:
```
That is good to know because I love tea much more than coffee anyway. What is your favorite drink in the morning?

Fix: She doesn't like coffee. || Gunakan "doesn't" untuk subjek tunggal orang ketiga (she/he/it) dalam present tense. || subject_verb_agreement
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E4 — en (fix)

Input: I am agree with you.

Provider: gemini | Latensi: 5.21 detik

Jawaban Lengkap LLM:
```
I am glad we have the same thought about this! It is always nice when we can agree on something. What topic do you want to talk about today?

Fix: I agree with you. || "Agree" adalah kata kerja, jadi tidak perlu menggunakan "am". || present_tense
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E5 — en (nofix)

Input: I went to school yesterday.

Provider: gemini | Latensi: 17.00 detik

Jawaban Lengkap LLM:
```
That is great! I hope you had a good day at school yesterday. Did you learn anything interesting in your classes?
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E6 — en (nofix)

Input: Can you recommend a good restaurant near here?

Provider: gemini | Latensi: 18.26 detik

Jawaban Lengkap LLM:
```
I would love to help you find a great place to eat! There is a wonderful Italian restaurant just around the corner that serves amazing pasta. What kind of food are you in the mood for today?
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E7 — en (fix)

Input: aku mau order coffee, tapi gimana ya bilangnya?

Provider: gemini | Latensi: 21.66 detik

Jawaban Lengkap LLM:
```
You can say, "Can I get a coffee, please?" or "I'd like a coffee, please." Both of those sound very natural and polite! What kind of coffee do you want to order?

Fix: I want to order coffee, but how do I say it? || Kata "aku mau" dan "gimana ya bilangnya" dapat diterjemahkan menjadi "I want to" dan "how do I say it". || code_mixing
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### E8 — en (ngawur)

Input: asdf obama purple tomorrow

Provider: gemini | Latensi: 20.36 detik

Jawaban Lengkap LLM:
```
That sounds like a very random mix of words! Did you mean to type something else, or are you just testing me? What would you like to talk about today?
```

Hasil pustaka:
- -

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### Z1 — zh (nofix)

Input: 你好，我叫Roy，我想学中文。

Provider: gemini | Latensi: 46.61 detik

Jawaban Lengkap LLM:
```
你好，Roy！很高兴认识你，我也很乐意教你中文。

Pinyin: Nǐ hǎo, Roy! Hěn gāoxìng rènshí nǐ, wǒ yě hěn lèyì jiāo nǐ Zhōngwén.
Arti: Halo, Roy! Senang berkenalan denganmu, aku juga sangat senang mengajarimu bahasa Mandarin.

你为什么想学中文呢？
```

Hasil pustaka:
- pypinyin: pustaka tidak terpasang

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### Z2 — zh (nofix)

Input: Wo xihuan chi fan.

Provider: gemini | Latensi: 16.40 detik

Jawaban Lengkap LLM:
```
我也喜欢吃饭，这是每天最重要的事情！你最喜欢吃什么菜呢？

Pinyin: Wǒ yě xǐhuān chī fàn, zhè shì měitiān zuì zhòngyào de shìqíng! Nǐ zuì xǐhuān chī shénme cài ne?

Arti: Saya juga suka makan, ini adalah hal paling penting setiap hari! Kamu paling suka makan lauk apa?
```

Hasil pustaka:
- pypinyin: pustaka tidak terpasang

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### Z3 — zh (fix)

Input: 我去学校昨天。

Provider: gemini | Latensi: 48.39 detik

Jawaban Lengkap LLM:
```
你昨天去学校做什么了？那里热闹吗？你今天还要去吗？
Pinyin: Nǐ zuótiān qù xuéxiào zuò shénme le? Nàlǐ rènao ma? Nǐ jīntiān hái yào qù ma?
Arti: Kamu kemarin ke sekolah melakukan apa? Di sana ramai tidak? Apakah kamu hari ini harus pergi lagi?

Fix: 我昨天去学校了。 || Kata keterangan waktu (昨天) dalam bahasa Mandarin diletakkan sebelum kata kerja, bukan di akhir kalimat. || word_order
```

Hasil pustaka:
- pypinyin: pustaka tidak terpasang

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### Z4 — zh (fix)

Input: 我有三个书。

Provider: gemini | Latensi: 53.65 detik

Jawaban Lengkap LLM:
```
太棒了！请问你最喜欢哪一本书？

Pinyin: Tài bàng le! Qǐngwèn nǐ zuì xǐhuān nǎ yī běn shū?
Arti: Luar biasa! Kalau boleh tahu, buku mana yang paling kamu sukai?

Fix: 我有三本书。 || Gunakan kata penggolong (量词) "本" (běn) untuk benda berupa buku, bukan "个" (gè). || word_choice
```

Hasil pustaka:
- pypinyin: pustaka tidak terpasang

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### Z5 — zh (fix)

Input: 他是很高。

Provider: gemini | Latensi: 7.63 detik

Jawaban Lengkap LLM:
```
他很高。在中文里，“是”通常不和形容词一起使用。你想用“很高”来形容谁呢？

Pinyin: Tā hěn gāo. Zài zhōngwén lǐ, "shì" tōngcháng bù hé xíngróngcí yīqǐ shǐyòng. Nǐ xiǎng yòng "hěn gāo" lái xíngróng shéi ne?

Arti: Dia sangat tinggi. Dalam bahasa Mandarin, kata "shì" biasanya tidak digunakan bersama kata sifat. Siapa yang ingin kamu gambarkan sebagai "sangat tinggi"?

Fix: 他很高。 || Kata "是" (shì) tidak digunakan sebelum kata sifat seperti "高" (gāo), cukup gunakan kata hubung seperti "很" (hěn). || word_choice
```

Hasil pustaka:
- pypinyin: pustaka tidak terpasang

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### Z6 — zh (ngawur)

Input: 苹果 电脑 昨天 红色 啊

Provider: gagal | Latensi: 1.88 detik
Error: Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env.

Jawaban Lengkap LLM:
```
(tidak ada balasan)
```

Hasil pustaka:
- pypinyin: pustaka tidak terpasang

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J1 — ja (nofix)

Input: Watashi wa gakusei desu.

Provider: gagal | Latensi: 1.67 detik
Error: Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env.

Jawaban Lengkap LLM:
```
(tidak ada balasan)
```

Hasil pustaka:
- cutlet: tidak dapat dihitung

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J2 — ja (nofix)

Input: 今日はいい天気ですね。

Provider: gagal | Latensi: 1.84 detik
Error: Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env.

Jawaban Lengkap LLM:
```
(tidak ada balasan)
```

Hasil pustaka:
- cutlet: tidak dapat dihitung

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J3 — ja (fix)

Input: 私は学校を行きます。

Provider: gagal | Latensi: 1.77 detik
Error: Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env.

Jawaban Lengkap LLM:
```
(tidak ada balasan)
```

Hasil pustaka:
- cutlet: tidak dapat dihitung

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J4 — ja (fix)

Input: 私は日本語を話すができます。

Provider: gagal | Latensi: 1.71 detik
Error: Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env.

Jawaban Lengkap LLM:
```
(tidak ada balasan)
```

Hasil pustaka:
- cutlet: tidak dapat dihitung

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J5 — ja (fix)

Input: 昨日、友達と映画を見ます。

Provider: gagal | Latensi: 1.78 detik
Error: Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env.

Jawaban Lengkap LLM:
```
(tidak ada balasan)
```

Hasil pustaka:
- cutlet: tidak dapat dihitung

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

### J6 — ja (ngawur)

Input: りんご パソコン 昨日 赤い ね

Provider: gemini | Latensi: 14.86 detik

Jawaban Lengkap LLM:
```
昨日買った赤くて新しいパソコンですね！
とても格好いいです。

Romaji: Kinou katta akakute atarashii pasokon desu ne! Totemo kakkoii desu.
Arti: Laptop merah yang kamu beli kemarin ya! Keren sekali.

どのようなパソコンですか？
```

Hasil pustaka:
- cutlet: beda

| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |
|---|---|---|
| | | |

## Catatan
- Pemeriksaan otomatis (a) sampai (d) adalah informasi pembantu, bukan penentu satu-satunya kualitas.
- Arti (baris 'Arti:') dan kebenaran koreksi ('Fix:') harus divalidasi secara manual di kolom yang disediakan.
- Jika panggilan gagal (misal kunci API belum diisi atau jaringan mati), provider dan latensi ditulis sebagai gagal, dan kasus berikutnya tetap dipanggil.
- Tidak ada kunci API yang dicetak atau disimpan dalam laporan ini.
