from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

CHATBASE_API_KEY = os.getenv('CHATBASE_API_KEY')
CHATBASE_CHATBOT_ID = os.getenv('CHATBASE_CHATBOT_ID')
CHATBASE_API_URL = "https://www.chatbase.co/api/v1/chat"

# Store conversation history
conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    user_message = request.json.get("message")
    
    # Add user's message to the conversation history
    conversation_history.append({"content": user_message, "role": "user"})
    
    payload = {
        "messages": conversation_history,
        "chatbotId": CHATBASE_CHATBOT_ID,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {CHATBASE_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(CHATBASE_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        assistant_reply = response.json().get("text")
        
        # Add assistant's reply to the conversation history
        conversation_history.append({"content": assistant_reply, "role": "assistant"})
        
        return jsonify({"reply": assistant_reply})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Bind to 0.0.0.0 for Render and fallback to 127.0.0.1 locally
    host = "0.0.0.0" if os.getenv("RENDER") else "127.0.0.1"
    port = int(os.getenv("PORT", 5000))  # Render sets PORT as an environment variable
    debug = os.getenv("FLASK_ENV") == "development"
    
    app.run(debug=debug, host=host, port=port)
