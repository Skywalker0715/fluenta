# Evaluasi Model Cadangan Groq (Live)

Hanya fungsi jalur Groq yang dipanggil (Gemini tidak disentuh). Maksimal 8 panggilan, jeda 3 detik.

## Hasil per Kasus

### Past tense error
- Pesan: Yesterday I go to the market
- Provider: groq
```
I understand. You went to the market yesterday. What did you buy?  
Fix: Yesterday I went to the market. || Kalimat harus memakai past tense 'went' karena 'go' adalah present tense, dan kata 'yesterday' menunjukkan waktu lampau. || past_tense
```

### Article error
- Pesan: I have cat
- Provider: groq
```
That's nice! Cats are great pets. Do you have a name for it?  
Fix: I have a cat. || Karena kata benda tunggal yang dapat dihitung harus didahului artikel tak tentu 'a'. || articles
```

### Subject-verb agreement error
- Pesan: She go to school
- Provider: groq
```
You should say “She goes to school.” It’s the present simple for a habit. Do you like going to school?

Fix: She goes to school. || Kata kerja harus sesuai dengan subjek orang ketiga tunggal, jadi tambahkan -s pada “go”. || subject_verb_agreement
```

### Correct sentence
- Pesan: Hello, how are you today?
- Provider: groq
```
I'm good, thank you! How about you? What would you like to talk about today?
```

### Mandarin 1
- Pesan: Ni hao ma?
- Provider: groq
```
我很好，你呢？  
Wǒ hěn hǎo, nǐ ne? || I am fine, how about you?
```

### Japanese 1
- Pesan: Konnichiwa
- Provider: groq
```
Hello! How are you today? What would you like to talk about?
```

### Code mixing
- Pesan: aku mau order coffee, tapi gimana ya bilangnya?
- Provider: groq
```
You can say, “I would like to order a coffee.”  
Or simply, “Can I have a coffee?”  
Which phrase sounds better to you?
```

### Preposition error
- Pesan: I am in Monday
- Provider: groq
```
Got it, today is Monday. How are you feeling about this week?  
Fix: It is Monday. || Untuk menyatakan hari, gunakan 'It is' dan tidak perlu preposisi 'in' atau 'on'. || prepositions
```

## Catatan
- Tidak ada API key yang tercantum dalam laporan ini.
- Semua panggilan menggunakan fungsi internal `_ask_tutor_groq` dari `services/llm.py`.
- System prompt sama dengan Gemini, ditambah aturan tambahan untuk Groq.