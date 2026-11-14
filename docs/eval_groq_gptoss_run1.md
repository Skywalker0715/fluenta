# Evaluasi LLM Cadangan (Groq)

Skor: 9/14
Rata-rata latensi: 1.51 detik

## Tabel Hasil per Kasus

| ID | Bahasa | Uji | PASS/FAIL | Alasan | Latensi (s) | Status HTTP |
|----|--------|-----|-----------|--------|-------------|-------------|
| E1 | en | Past tense error | FAIL | penjelasan bukan bahasa Indonesia | 1.799 | 200 |
| E2 | en | Article error | FAIL | penjelasan bukan bahasa Indonesia | 1.048 | 200 |
| E3 | en | Preposition error | PASS | PASS | 1.607 | 200 |
| E4 | en | Subject-verb agreement error | FAIL | penjelasan bukan bahasa Indonesia | 1.997 | 200 |
| E5 | en | Plural/singular error | PASS | PASS | 1.451 | 200 |
| E6 | en | Word order error | FAIL | penjelasan bukan bahasa Indonesia | 1.586 | 200 |
| C1 | en | Correct sentence 1 | PASS | PASS | 0.876 | 200 |
| C2 | en | Correct sentence 2 | PASS | PASS | 0.979 | 200 |
| C3 | en | Correct sentence 3 | PASS | PASS | 1.006 | 200 |
| Z1 | zh | Mandarin 1 | PASS | PASS | 1.875 | 200 |
| Z2 | zh | Mandarin 2 | PASS | PASS | 1.858 | 200 |
| J1 | ja | Japanese 1 | PASS | PASS | 1.651 | 200 |
| J2 | ja | Japanese 2 | PASS | PASS | 1.88 | 200 |
| M1 | en | Code mixing | FAIL | penjelasan bukan bahasa Indonesia | 1.486 | 200 |

## Ringkasan Skor
- Total kasus: 14
- Lulus: 9
- Gagal: 5
- Rata-rata latensi: 1.51 detik

## Daftar FAIL
- E1 (Past tense error): penjelasan bukan bahasa Indonesia
- E2 (Article error): penjelasan bukan bahasa Indonesia
- E4 (Subject-verb agreement error): penjelasan bukan bahasa Indonesia
- E6 (Word order error): penjelasan bukan bahasa Indonesia
- M1 (Code mixing): penjelasan bukan bahasa Indonesia

## 3 Contoh Jawaban Mentah Paling Buruk

### J2 - Japanese 2
- Pesan pengguna: Watashi wa gakusei desu
- Status HTTP: 200
- Error: -
- Latensi: 1.88 detik
```
{"id":"chatcmpl-193b9861-9f13-4ac2-9daa-67f00c621649","object":"chat.completion","created":1794638882,"model":"openai/gpt-oss-120b","choices":[{"index":0,"message":{"role":"assistant","content":"そうですか。どんな科目を勉強していますか？\n\nRomaji: Sou desu ka. Don'na kamoku o benkyou shiteimasu ka?\n\nArti: Begitu ya. Mata pelajaran apa yang kamu pelajari?","reasoning":"We need to respond in Japanese, simple English max 3 short sentences, end with a follow-up question. Wait: The instruction says: \"You are a friendly English tutor and conversation partner for an Indonesian learner. Reply in simple English, maximum 3 short sentences, and end with one follow-up question.\" Then later: \"Reply in Japanese. Add a line starting exactly with 'Romaji: ' and a line starting exactly with 'Arti: ' (Indonesian meaning).\" So we need to produce Japanese text (presumably the main reply) but also include Romaji and Arti lines. The main reply must be in simple English? There's conflict. The developer says: \"Reply in Ja
```

### Z1 - Mandarin 1
- Pesan pengguna: Ni hao ma?
- Status HTTP: 200
- Error: -
- Latensi: 1.875 detik
```
{"id":"chatcmpl-a2cc017a-4a4f-490d-ba8e-1a0c6751ed1c","object":"chat.completion","created":1794638867,"model":"openai/gpt-oss-120b","choices":[{"index":0,"message":{"role":"assistant","content":"我很好，谢谢。你今天过得怎么样？\n\nPinyin: Wǒ hěn hǎo, xièxiè. Nǐ jīntiān guò de zěnme yàng?\n\nArti: Saya baik, terima kasih. Bagaimana hari Anda hari ini?","reasoning":"We need to respond in simple English, max 3 short sentences, end with a follow-up question. But also reply in Mandarin Chinese (Simplified). Wait contradictory: The instruction says \"Reply in Mandarin Chinese (Simplified). Add a line starting exactly with 'Pinyin: ' and a line starting exactly with 'Arti: ' (Indonesian meaning).\" Also earlier: \"You are a friendly English tutor and conversation partner for an Indonesian learner. Reply in simple English, maximum 3 short sentences, and end with one follow-up question.\" So we need to combine? Probably we need to give English response (simple English, max 3 sentences, ending with follow-up qu
```

### Z2 - Mandarin 2
- Pesan pengguna: Wo xihuan chi fan
- Status HTTP: 200
- Error: -
- Latensi: 1.858 detik
```
{"id":"chatcmpl-1696e31c-faf0-4e24-8a32-0dfee2a1fea2","object":"chat.completion","created":1794638872,"model":"openai/gpt-oss-120b","choices":[{"index":0,"message":{"role":"assistant","content":"很高兴听到你喜欢吃饭。你平时喜欢吃什么菜？\n\nPinyin: Hěn gāoxìng tīngdào nǐ xǐhuān chīfàn. Nǐ píngshí xǐhuān chī shénme cài?\n\nArti: Senang mendengar kamu suka makan. Kamu biasanya suka makan apa?","reasoning":"We need to respond as a friendly English tutor and conversation partner for an Indonesian learner, reply in simple English, max 3 short sentences, end with a follow-up question. But also reply in Mandarin Chinese (Simplified). Wait conflict: instructions say \"Reply in simple English, maximum 3 short sentences, and end with one follow-up question.\" Then later: \"Reply in Mandarin Chinese (Simplified). Add a line starting exactly with 'Pinyin: ' and a line starting exactly with 'Arti: ' (Indonesian meaning). Place any Fix line last.\"\n\nSo we need to produce response in Mandarin Chinese (Simplified) (the 
```

## Catatan
- Tidak ada API key yang tercantum dalam laporan ini.
- Semua pemanggilan API menggunakan `requests` ke endpoint Groq.
- System prompt menggunakan `_build_system_prompt` dari `services/llm.py` yang sama dengan Gemini.