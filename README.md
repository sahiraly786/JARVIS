# JARVIS — Setup Guide

## Pehli baar setup karo

### 1. Libraries install karo
```
pip install -r requirements.txt
```

### 2. API Keys set karo
`.env` file kholo aur apni actual keys daalo:
```
GEMINI_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
WEATHER_API_KEY=a707...
```

**Keys kahan milti hain:**
- Gemini  → https://aistudio.google.com/apikey
- Groq    → https://console.groq.com/keys
- Weather → https://www.weatherapi.com (free account)

### 3. Jarvis chalao
```
python Jarvis.py
```

### 4. Browser mein kholo
```
http://localhost:5000
```

---

## Project Structure
```
Jarvis/
├── Jarvis.py              ← Sirf yahi chalao
├── .env                   ← API keys (Git mein mat daalo!)
├── .gitignore
├── requirements.txt
├── templates/
│   └── index.html         ← Frontend (Flask serve karta hai)
└── Datacollect/           ← AI responses save hoti hain (auto-create)
```

---

## Kya kya kar sakta hai Jarvis?
- **"What time is it"** → current time
- **"What is the date"** → aaj ki date
- **"Weather in Lahore"** → mausam
- **"Open YouTube"** → YouTube browser mein khulta hai
- **"Open Google / Gmail / WhatsApp / GitHub"** → websites khulti hain
- **Koi bhi sawal** → Gemini ya Groq se jawab
- **🎤 Mic button** → voice input (Chrome/Edge mein kaam karta hai)
- **Browser TTS** → Jarvis browser mein bolta hai (pyttsx3 nahi chahiye!)

---

## Purane bugs jo fix hue
1. Wrong subprocess chal raha tha (_jarvis_runner demo run ho raha tha)
2. pyttsx3 server pe chal raha tha, browser pe nahi — ab Web Speech API use karta hai
3. script.js static/ mein nahi tha — ab sab index.html mein integrate hai
4. Frontend Flask se connected nahi tha — ab /ask route properly kaam karta hai
5. API keys hardcoded thi — ab .env file use hoti hai
