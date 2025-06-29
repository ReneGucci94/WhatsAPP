from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

estado_usuarios = {}

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    user_id = request.values.get("From")
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if user_id not in estado_usuarios:
        estado_usuarios[user_id] = {"paso": "esperando_sucursal"}
        msg.body("¡Qué onda, compa! Bienvenido a *Dogos El Compadre* 🌭🔥\n¿Pa’ qué sucursal va a ser el dogo?\n\n👉 *Jardines*\n👉 *Pueblitos*\n👉 *Puerta Real*")
        return str(resp)

    if estado_usuarios[user_id]["paso"] == "esperando_sucursal":
        if "jardines" in incoming_msg:
            sucursal = "Jardines"
        elif "pueblitos" in incoming_msg:
            sucursal = "Pueblitos"
        elif "puerta" in incoming_msg:
            sucursal = "Puerta Real"
        else:
            msg.body("No caché bien eso, compa. Escríbeme: *Jardines*, *Pueblitos* o *Puerta Real*.")
            return str(resp)

        estado_usuarios[user_id]["sucursal"] = sucursal
        estado_usuarios[user_id]["paso"] = "sucursal_confirmada"

        msg.body(f"¡Fierro, pa’ *{sucursal}*! 🔥 Ahora, ármate el dogo a tu gusto:\n\n🌭 Sencillo\n🌭🌭 Doble\n📏 De a Metro\n🥐 Churro-Dogo")
        return str(resp)

    msg.body("Espérame compa, todavía estoy calentando la plancha 🧠. Próximamente podrás elegir tu dogo aquí mismo.")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
