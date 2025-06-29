from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    """Temporary minimal webhook endpoint."""
    return "ok", 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
