from flask import Flask, request, jsonify
import openai
import os
import requests

app = Flask(__name__)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
CALENDAR_ID = os.getenv("CALENDAR_ID")
GHL_WEBHOOK_URL = os.getenv("GHL_WEBHOOK_URL")

@app.route("/webhook", methods=["POST"])
def handle_call():
    data = request.json
    user_text = data.get("speech", "")
    language = detect_language(user_text)

    response = generate_response(user_text, language)
    post_to_ghl(data.get("contact_id"), user_text, response)

    return jsonify({"response": response})

def detect_language(text):
    # Basic language detection placeholder
    if any(char in text for char in ["।", "ह"]):
        return "hindi"
    elif any(char in text for char in ["ਾ", "ਕ"]):
        return "punjabi"
    return "english"

def generate_response(user_text, lang):
    prompt = f"Respond in {lang}: {user_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def post_to_ghl(contact_id, user_text, response):
    if not GHL_WEBHOOK_URL or not contact_id:
        return
    payload = {
        "contact_id": contact_id,
        "message": user_text,
        "ai_response": response
    }
    try:
        requests.post(GHL_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Error posting to GHL: {e}")

if __name__ == "__main__":
    app.run(debug=True)