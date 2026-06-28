from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
import re

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Flask session secret key
app.secret_key = os.getenv("SECRET_KEY", "default_secret")

# Load OpenAI API Key and model
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# ---------------------------
# Initialize conversation
# ---------------------------
def init_conversation():
    if "messages" not in session:
        session["messages"] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for farmers. "
                    "Always respond only in simple plain text. "
                    "Never use formatting like **bold**, *, -, —, lists, bullets, or numbers. "
                    "Do not format sections or headings. "
                    "Just write natural continuous sentences without symbols."
                ),
            }
        ]


# ---------------------------
# Remove formatting (backup safety)
# ---------------------------
def clean_text(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)   # remove **bold**
    text = re.sub(r"\*(.*?)\*", r"\1", text)       # remove *italics*
    text = re.sub(r"^- ", "", flags=re.MULTILINE, string=text)  # remove bullet "- "
    text = re.sub(r"• ", "", text)                 # remove bullet dot
    text = re.sub(r"\n\d+\.\s*", "\n", text)       # remove numbered list
    text = re.sub(r"\n-+", "\n", text)             # remove "---"
    return text.strip()


# ---------------------------
# Home Route
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------
# Chat API Route
# ---------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    init_conversation()
    data = request.get_json() or {}
    user_text = data.get("message", "").strip()

    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    # Add user message to session
    messages = session["messages"]
    messages.append({"role": "user", "content": user_text})

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.4
        )

        # Extract message
        assistant_reply = response.choices[0].message.content

        # Backup cleaning
        assistant_reply = clean_text(assistant_reply)

        # Save assistant message
        messages.append({"role": "assistant", "content": assistant_reply})
        session["messages"] = messages

        return jsonify({"reply": assistant_reply})

    except Exception as e:
        print("------ OPENAI ERROR ------")
        print(e)
        print("---------------------------")
        return jsonify({"error": "LLM request failed."}), 500


# ---------------------------
# Run Flask
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
