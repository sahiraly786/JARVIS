"""
Jarvis.py — Sirf yeh ek file chalao: python Jarvis.py
Browser mein kholo: http://localhost:5000

HOW IT WORKS:
- /          → HTML page serve karta hai
- /ask       → User ka text leke AI se jawab deta hai (main route)
- /weather   → Weather fetch karta hai
- /open-site → Browser mein website kholta hai
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
import webbrowser, datetime, os, sys, requests


# ── Load API keys from .env ──

GEMINI_KEY  = ("AQ.Ab8RN6KrD7tv8yZE0iwDry2SZzZ_evQzeQUBbRYkGySqYVItpQ")
GROQ_KEY    = ("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")
WEATHER_KEY = ("a707959a53c649caafc111142261904")

# ── AI Clients ──
from groq import Groq
from google import genai

gemini_client = genai.Client(api_key=GEMINI_KEY)
groq_client   = Groq(api_key=GROQ_KEY)

app = Flask(__name__)
CORS(app)  # Allow frontend to call backend even from different port


# ══════════════════════════════════════════
#  AI FUNCTIONS
# ══════════════════════════════════════════

def gemini_ask(prompt):
    """Gemini se jawab lo"""
    response = ""
    try:
        for chunk in gemini_client.models.generate_content_stream(
            model="gemini-3-flash-preview", contents=prompt
        ):
            if chunk.text:
                response += chunk.text

        # Datacollect folder mein save karo
        if response:
            if not os.path.exists("Datacollect"):
                os.mkdir("Datacollect")
            safe_name = prompt[:20].replace(' ', '_').replace('/', '_')
            with open(f"Datacollect/{safe_name}.txt", "w", encoding="utf-8") as f:
                f.write(response)
    except Exception as e:
        print(f"[Gemini ERROR] {e}")
        return None
    return response


def groq_ask(prompt):
    """Groq se jawab lo (Gemini ka backup)"""
    response = ""
    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",   # stable model
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
    except Exception as e:
        print(f"[Groq ERROR] {e}")
        return None
    return response


def get_ai_response(prompt):
    """Pehle Gemini try karo, agar fail ho toh Groq"""
    print(f"[SYSTEM] Gemini se pooch raha hoon...")
    response = gemini_ask(prompt)

    if not response or "RESOURCE_EXHAUSTED" in str(response) or len(response.strip()) == 0:
        print("[SYSTEM] Gemini ne kaam nahi kiya, Groq pe switch kar raha hoon...")
        response = groq_ask(prompt)

    return response or "Mujhe koi response nahi mila."


def get_weather(city):
    """WeatherAPI se mausam lo"""
    try:
        res = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key={WEATHER_KEY}&q={city}",
            timeout=5
        )
        data = res.json()
        if "error" in data:
            return f"'{city}' city nahi mili. Dobara try karo."
        temp = data['current']['temp_c']
        cond = data['current']['condition']['text']
        return f"{city} mein abhi {temp}°C hai aur {cond} hai."
    except Exception as e:
        return "Weather fetch nahi ho saka. Internet check karo."


# ══════════════════════════════════════════
#  COMMAND PARSER
# ══════════════════════════════════════════

SITES = [
    ["youtube",     "https://www.youtube.com"],
    ["google",      "https://www.google.com"],
    ["wikipedia",   "https://www.wikipedia.org"],
    ["whatsapp",    "https://web.whatsapp.com"],
    ["gmail",       "https://mail.google.com"],
    ["chatgpt",     "https://chatgpt.com"],
    ["gemini",      "https://gemini.google.com/app"],
    ["github",      "https://github.com"],
    ["outlook",     "https://outlook.live.com"],
    ["maju portal", "https://nexus.maju.edu.pk/web/login"],
    ["maju",        "https://jinnah.edu"],
]

def process_command(query):
    """
    User ka query parse karo aur jawab do.
    Returns dict: { "response": str, "action": str|None, "action_data": any }
    """
    q = query.lower().strip()

    # ── Time ──
    if "time" in q:
        t = datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"Abhi {t} baj rahe hain.", "action": None}

    # ── Date ──
    if "date" in q or "aaj" in q:
        d = datetime.datetime.now().strftime("%A, %d %B %Y")
        return {"response": f"Aaj {d} hai.", "action": None}

    # ── Jarvis name ──
    if "your name" in q or "tera naam" in q or "tumhara naam" in q:
        return {"response": "Mera naam Jarvis hai. Main aapka AI assistant hoon.", "action": None}

    # ── Weather ──
    if "weather" in q or "mausam" in q:
        # City dhundho query mein
        words = q.replace("weather", "").replace("mausam", "").replace("in", "").replace("of", "").strip()
        city = words if words else "Karachi"
        weather_msg = get_weather(city)
        return {"response": weather_msg, "action": None}

    # ── Open website ──
    for site in SITES:
        if f"open {site[0]}" in q:
            return {
                "response": f"Theek hai, {site[0]} khol raha hoon!",
                "action": "open_url",
                "action_data": site[1]
            }

    # ── AI se poochho ──
    response = get_ai_response(query)
    return {"response": response, "action": None}


# ══════════════════════════════════════════
#  FLASK ROUTES
# ══════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    """
    Frontend se query aati hai, process karke jawab dete hain.
    Request body: { "query": "user ka sawal" }
    Response:     { "response": "...", "action": null | "open_url", "action_data": "..." }
    """
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Query missing"}), 400

    query = data["query"].strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    print(f"[USER] {query}")
    result = process_command(query)
    print(f"[JARVIS] {result['response'][:80]}...")
    return jsonify(result)


@app.route("/weather", methods=["GET"])
def weather():
    city = request.args.get("city", "Karachi")
    return jsonify({"weather": get_weather(city)})


# ══════════════════════════════════════════
#  START SERVER
# ══════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  JARVIS chal raha hai!")
    print("  Browser mein kholo: http://localhost:5000")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
