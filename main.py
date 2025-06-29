from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Memoria temporal por usuario
estado_usuarios = {}

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    user_id = request.values.get("From")
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    # Si no hay contexto previo, comenzamos con saludo + pregunta de sucursal
    if user_id not in estado_usuarios:
        estado_usuarios[user_id] = {"paso": "esperando_sucursal"}
        msg.body(
            "\u00a1Qu\u00e9 onda, compa! Bienvenido a *Dogos El Compadre* \ud83c\udf2d\ud83d\udd25\n\u00bfPa’ qu\u00e9 sucursal va a ser el dogo?\n\n\ud83d\udc49 *Jardines*\n\ud83d\udc49 *Pueblitos*\n\ud83d\udc49 *Puerta Real*"
        )
        return str(resp)

    # Paso 1: Usuario ya est\u00e1 eligiendo sucursal
    if estado_usuarios[user_id]["paso"] == "esperando_sucursal":
        if "jardines" in incoming_msg:
            sucursal = "Jardines"
        elif "pueblitos" in incoming_msg:
            sucursal = "Pueblitos"
        elif "puerta real" in incoming_msg or "puerta" in incoming_msg:
            sucursal = "Puerta Real"
        else:
            msg.body(
                "No entend\u00ed bien la sucursal, compa. Escr\u00edbeme: *Jardines*, *Pueblitos* o *Puerta Real*."
            )
            return str(resp)

        estado_usuarios[user_id]["sucursal"] = sucursal
        estado_usuarios[user_id]["paso"] = "sucursal_confirmada"

        msg.body(
            f"\u00a1Fierro, pa’ *{sucursal}*! \ud83d\udd25 Ahora, \u00e1rmate el dogo a tu gusto:\n\n\ud83c\udf2d Sencillo\n\ud83c\udf2d\ud83c\udf2d Doble\n\ud83d\udcbf De a Metro\n\ud83e\udd50 Churro-Dogo"
        )
        return str(resp)

    # Si ya pas\u00f3 el paso 1 pero no est\u00e1 implementado el siguiente paso
    msg.body(
        "Esp\u00e9rame compa, todav\u00eda estoy calentando la plancha \ud83e\udde0. Pr\u00f3ximamente podr\u00e1s elegir tu dogo aqu\u00ed mismo."
    )
    return str(resp)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
