from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "hola" in incoming_msg:
        msg.body("¡Qué onda compa! Bienvenido a *Dogos El Compadre* 🌭🔥 ¿Listo pa' armarte el mejor dogo de tu vida?")
    elif "menú" in incoming_msg:
        msg.body("🧾 *Menú:*\n- Dogo Sencillo $45\n- Dogo con Todo $60\n- Dogo de a Metro $400\n¿Le metemos doble salchicha o con eso tienes?")
    elif "ubicación" in incoming_msg or "dónde están" in incoming_msg:
        msg.body("📍 Tenemos 3 sucursales:\n1. Jardines\n2. Pueblitos\n3. Puerta Real\nDime cuál quieres y te paso el mapa.")
    else:
        msg.body("No caché bien eso, compa. Prueba con: 'menú', 'ubicación' o 'hola' pa' empezar 🔥")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
