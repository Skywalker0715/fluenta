# Evaluasi LLM Cadangan (Groq)

Skor: 9/14
Rata-rata latensi: 1.53 detik

## Tabel Hasil per Kasus

| ID | Bahasa | Uji | PASS/FAIL | Alasan | Latensi (s) | Status HTTP |
|----|--------|-----|-----------|--------|-------------|-------------|
| E1 | en | Past tense error | PASS | PASS | 1.64 | 200 |
| E2 | en | Article error | FAIL | penjelasan bukan bahasa Indonesia | 1.203 | 200 |
| E3 | en | Preposition error | FAIL | penjelasan bukan bahasa Indonesia | 1.232 | 200 |
| E4 | en | Subject-verb agreement error | PASS | PASS | 1.348 | 200 |
| E5 | en | Plural/singular error | FAIL | penjelasan bukan bahasa Indonesia | 1.308 | 200 |
| E6 | en | Word order error | FAIL | penjelasan bukan bahasa Indonesia | 1.289 | 200 |
| C1 | en | Correct sentence 1 | PASS | PASS | 0.931 | 200 |
| C2 | en | Correct sentence 2 | PASS | PASS | 0.931 | 200 |
| C3 | en | Correct sentence 3 | PASS | PASS | 0.825 | 200 |
| Z1 | zh | Mandarin 1 | PASS | PASS | 2.082 | 200 |
| Z2 | zh | Mandarin 2 | PASS | PASS | 2.46 | 200 |
| J1 | ja | Japanese 1 | PASS | PASS | 2.377 | 200 |
| J2 | ja | Japanese 2 | PASS | PASS | 2.023 | 200 |
| M1 | en | Code mixing | FAIL | penjelasan bukan bahasa Indonesia | 1.77 | 200 |

## Ringkasan Skor
- Total kasus: 14
- Lulus: 9
- Gagal: 5
- Rata-rata latensi: 1.53 detik

## Daftar FAIL
- E2 (Article error): penjelasan bukan bahasa Indonesia
- E3 (Preposition error): penjelasan bukan bahasa Indonesia
- E5 (Plural/singular error): penjelasan bukan bahasa Indonesia
- E6 (Word order error): penjelasan bukan bahasa Indonesia
- M1 (Code mixing): penjelasan bukan bahasa Indonesia

## 3 Contoh Jawaban Mentah Paling Buruk

### Z2 - Mandarin 2
- Pesan pengguna: Wo xihuan chi fan
- Status HTTP: 200
- Error: -
- Latensi: 2.46 detik
```
{"id":"chatcmpl-c9b173b4-3158-4515-885f-1426644d7dac","object":"chat.completion","created":1794640977,"model":"openai/gpt-oss-120b","choices":[{"index":0,"message":{"role":"assistant","content":"我喜欢吃饭。  \n你最喜欢吃什么？  \nPinyin: Wǒ xǐhuān chī fàn.  \nArti: Saya suka makan.","reasoning":"We need to respond in simple English, max 3 short sentences, end with one follow-up question. But also reply in Mandarin Chinese (Simplified). Wait: The instruction says: \"Reply in Mandarin Chinese (Simplified). Add a line starting exactly with 'Pinyin: ' and a line starting exactly with 'Arti: ' (Indonesian meaning).\" Also earlier: \"You are a friendly English tutor and conversation partner for an Indonesian learner. Reply in simple English, maximum 3 short sentences, and end with one follow-up question.\" There's conflict: reply in English vs Mandarin Chinese. The later instruction (developer) overrides? Usually developer instructions have priority. The developer says: \"Reply in Mandarin Chinese (Simpl
```

### J1 - Japanese 1
- Pesan pengguna: Konnichiwa
- Status HTTP: 200
- Error: -
- Latensi: 2.377 detik
```
{"id":"chatcmpl-b07754bb-5d3b-494f-94cb-6360cb643630","object":"chat.completion","created":1794640983,"model":"openai/gpt-oss-120b","choices":[{"index":0,"message":{"role":"assistant","content":"こんにちは！今日は元気ですか？何について話したいですか？\n\nRomaji: Konnichiwa! Kyou wa genki desu ka? Nani ni tsuite hanashitai desu ka?  \nArti: Halo! Apa kabar hari ini? Topik apa yang ingin kamu bicarakan?","reasoning":"We need to respond as a friendly English tutor and conversation partner for an Indonesian learner. Reply in simple English, maximum 3 short sentences, and end with a follow-up question. Also reply in Japanese, with Romaji and Arti lines. The user's message: \"Konnichiwa\". That's Japanese greeting. We need to respond in simple English, max 3 short sentences, ending with a follow-up question. Also reply in Japanese. So we need to produce Japanese text (the main reply) then Romaji line and Arti line. The main reply must be simple English, max 3 short sentences, ending with a follow-up question. But also 
```

### Z1 - Mandarin 1
- Pesan pengguna: Ni hao ma?
- Status HTTP: 200
- Error: -
- Latensi: 2.082 detik
```
{"id":"chatcmpl-760f09b9-f189-48eb-9258-ae0fbd564008","object":"chat.completion","created":1794640972,"model":"openai/gpt-oss-120b","choices":[{"index":0,"message":{"role":"assistant","content":"我很好，谢谢。你呢？\n\nPinyin: Wǒ hěn hǎo, xièxiè. Nǐ ne?\n\nArti: Saya baik, terima kasih. Kamu bagaimana?","reasoning":"We need to respond as a friendly English tutor and conversation partner for an Indonesian learner. Reply in simple English, max 3 short sentences, end with a follow-up question. Must be in Mandarin Chinese (Simplified). Also add Pinyin line and Arti line. The user's message: \"Ni hao ma?\" That's Chinese greeting \"How are you?\" The user is Indonesian learner of English, but they wrote Chinese. We need to reply in simple English, but the instruction says \"Reply in Mandarin Chinese (Simplified).\" There's conflict: The role says you are a friendly English tutor and conversation partner, reply in simple English max 3 short sentences, end with follow-up question. Then later: \"Reply i
```

## Jawaban Lengkap Semua Kasus

### E1 - Past tense error
- Pesan pengguna: Yesterday I go to the market
- Model: openai/gpt-oss-120b
```
That sounds nice. Did you buy anything interesting? What did you buy?  
Fix: Yesterday I went to the market. || Gunakan past tense untuk menyatakan kejadian yang sudah terjadi || past_tense
```

### E2 - Article error
- Pesan pengguna: I have cat
- Model: openai/gpt-oss-120b
```
You have a cat, that's nice. What is its name?  
Fix: I have a cat || need article 'a' before singular countable noun || articles
```

### E3 - Preposition error
- Pesan pengguna: I am in Monday
- Model: openai/gpt-oss-120b
```
Sounds good, you’re on Monday. What do you plan to do that day?  

Fix: I am on Monday. || preposisi 'on' untuk hari || prepositions
```

### E4 - Subject-verb agreement error
- Pesan pengguna: She go to school
- Model: openai/gpt-oss-120b
```
She goes to school. Do you like going to school?  
Fix: She goes to school. || perjodohan subjek dan kata kerja || subject_verb_agreement
```

### E5 - Plural/singular error
- Pesan pengguna: I have two book
- Model: openai/gpt-oss-120b
```
You have two books. That's great. What will you read next?  
Fix: I have two books. || bentuk jamak || plural_singular
```

### E6 - Word order error
- Pesan pengguna: I like very much coffee
- Model: openai/gpt-oss-120b
```
I like coffee very much too. It's a wonderful drink. What do you usually drink with coffee?  
Fix: I like coffee very much. || adverb placement (word order) || word_order
```

### C1 - Correct sentence 1
- Pesan pengguna: Hello, how are you today?
- Model: openai/gpt-oss-120b
```
I'm good, thank you! How about you? What would you like to talk about today?
```

### C2 - Correct sentence 2
- Pesan pengguna: I am going to the library to study.
- Model: openai/gpt-oss-120b
```
That sounds good. The library is a quiet place. What subject are you studying?
```

### C3 - Correct sentence 3
- Pesan pengguna: The weather is very nice today.
- Model: openai/gpt-oss-120b
```
I'm glad you think the weather is nice. It's a great day for a walk. What do you like to do when the weather is nice?
```

### Z1 - Mandarin 1
- Pesan pengguna: Ni hao ma?
- Model: openai/gpt-oss-120b
```
我很好，谢谢。你呢？

Pinyin: Wǒ hěn hǎo, xièxiè. Nǐ ne?

Arti: Saya baik, terima kasih. Kamu bagaimana?
```

### Z2 - Mandarin 2
- Pesan pengguna: Wo xihuan chi fan
- Model: openai/gpt-oss-120b
```
我喜欢吃饭。  
你最喜欢吃什么？  
Pinyin: Wǒ xǐhuān chī fàn.  
Arti: Saya suka makan.
```

### J1 - Japanese 1
- Pesan pengguna: Konnichiwa
- Model: openai/gpt-oss-120b
```
こんにちは！今日は元気ですか？何について話したいですか？

Romaji: Konnichiwa! Kyou wa genki desu ka? Nani ni tsuite hanashitai desu ka?  
Arti: Halo! Apa kabar hari ini? Topik apa yang ingin kamu bicarakan?
```

### J2 - Japanese 2
- Pesan pengguna: Watashi wa gakusei desu
- Model: openai/gpt-oss-120b
```
はじめまして。あなたは学生ですね。何を勉強していますか？

Romaji: Hajimemashite. Anata wa gakusei desu ne. Nani o benkyou shiteimasu ka?

Arti: Senang bertemu denganmu. Kamu adalah pelajar, ya. Kamu sedang belajar apa?
```

### M1 - Code mixing
- Pesan pengguna: aku mau order coffee, tapi gimana ya bilangnya?
- Model: openai/gpt-oss-120b
```
You can say, “I would like a coffee, please.” That’s a polite way to order. Would you like to practice saying it?  

Fix: I want to order coffee, but how do I say it? || Gunakan “I would like a coffee, please” untuk memesan. || code_mixing
```

## Catatan
- Tidak ada API key yang tercantum dalam laporan ini.
- Semua pemanggilan API menggunakan `requests` ke endpoint Groq.
- System prompt menggunakan `_build_system_prompt` dari `services/llm.py` yang sama dengan Gemini.