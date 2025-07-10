from flask import Flask, request, jsonify, render_template, session
import firebase_admin
from firebase_admin import credentials, db
import requests
import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Firebase setup
cred = credentials.Certificate("automation.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://automation-6c03d-default-rtdb.firebaseio.com/"
})

OPENROUTER_API_KEY = "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"

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
        return "\ud83d\udce5 No reminders found."
    return "\n".join([f"\ud83d\udd14 {v['reminder']} (set at {v['time']})" for v in data.values()])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin_dashboard():
    messages = db.reference("analytics/chats").get() or {}
    reminders = db.reference("reminders").get() or {}
    return render_template("admin.html", messages=messages, reminders=reminders)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    user_email = "user@example.com"
    extra_response = ""

    db.reference("analytics/chats").push({
        "user": user_email,
        "message": user_input,
        "timestamp": datetime.datetime.now().isoformat()
    })

    if user_input.lower().startswith("remind me to"):
        save_reminder(user_email, user_input[12:].strip())
        extra_response += "\u2705 Reminder saved!\n\n"

    if user_input.lower() in ["show reminders", "show my reminders"]:
        extra_response += get_reminders(user_email) + "\n\n"

    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": (
                "You are an expert HR assistant. You help users with leave policies, job openings, scheduling, onboarding."
            )}
        ]

    session["history"].append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://chatbot.local",
                "X-Title": "HRBot"
            },
            json={"model": "mistralai/mistral-7b-instruct", "messages": session["history"]}
        )

        result = response.json()
        if "choices" in result:
            bot_reply = result["choices"][0]["message"]["content"]
            session["history"].append({"role": "assistant", "content": bot_reply})
            return jsonify({"response": extra_response + bot_reply})
        else:
            return jsonify({"response": "[OpenRouter Error] " + str(result)})

    except Exception as e:
        return jsonify({"response": f"[Exception] {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
