from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, db
import requests
import datetime

app = Flask(__name__)

# 🔐 Firebase setup
cred = credentials.Certificate("automation.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://automation-6c03d-default-rtdb.firebaseio.com/"
})

# 🔑 OpenRouter API key (replace with yours)
OPENROUTER_API_KEY = "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"  # 👈 Replace with actual key

# 🔁 Reminder functions
def save_reminder(user, text):
    ref = db.reference("reminders").child(user.replace("@", "_at_").replace(".", "_dot_"))
    ref.push({
        "reminder": text,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def get_reminders(user):
    ref = db.reference("reminders").child(user.replace("@", "_at_").replace(".", "_dot_"))
    data = ref.get()
    if not data:
        return "📭 No reminders found."
    return "\n".join([f"🔔 {v['reminder']} (set at {v['time']})" for v in data.values()])

# 🌐 Frontend route
@app.route("/")
def index():
    return render_template("index.html")

# 🤖 Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    user_email = "user@example.com"

    if user_input.lower().startswith("remind me to"):
        save_reminder(user_email, user_input[12:].strip())
        return jsonify({"response": "✅ Reminder saved!"})

    if user_input.lower() in ["show reminders", "show my reminders"]:
        return jsonify({"response": get_reminders(user_email)})

    # 🧠 Enhanced HR assistant system prompt
    messages = [
        {"role": "system", "content": (
            "You are an expert HR assistant. You help users with questions about leave policies, job openings, "
            "interview scheduling, onboarding, and internal HR procedures. "
            "Always be polite, professional, and clear. Answer based on standard HR practices."
        )},
        {"role": "user", "content": user_input}
    ]

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://chatbot.local",
                "X-Title": "HRBot"
            },
            json={"model": "mistralai/mistral-7b-instruct", "messages": messages}
        )

        result = response.json()
        if "choices" in result:
            return jsonify({"response": result["choices"][0]["message"]["content"]})
        else:
            return jsonify({"response": "[Error from OpenRouter] " + str(result)})

    except Exception as e:
        return jsonify({"response": f"[Exception] {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
