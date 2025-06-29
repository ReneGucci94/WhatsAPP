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

    estado = estado_usuarios[user_id]

    if estado["paso"] == "esperando_sucursal":
        if "jardines" in incoming_msg:
            estado["sucursal"] = "Jardines"
        elif "pueblitos" in incoming_msg:
            estado["sucursal"] = "Pueblitos"
        elif "puerta" in incoming_msg:
            estado["sucursal"] = "Puerta Real"
        else:
            msg.body("No caché bien eso, compa. Escríbeme: *Jardines*, *Pueblitos* o *Puerta Real*.")
            return str(resp)

        estado["paso"] = "esperando_dogo"
        msg.body(f"¡Fierro, pa’ *{estado['sucursal']}*! 🔥 Ahora, ármate el dogo a tu gusto:\n\n🌭 Sencillo\n🌭🌭 Doble\n📏 De a Metro\n🥐 Churro-Dogo")
        return str(resp)

    if estado["paso"] == "esperando_dogo":
        if "sencillo" in incoming_msg:
            estado["tipo_dogo"] = "Sencillo"
        elif "doble" in incoming_msg:
            estado["tipo_dogo"] = "Doble"
        elif "metro" in incoming_msg:
            estado["tipo_dogo"] = "De a Metro"
        elif "churro" in incoming_msg:
            estado["tipo_dogo"] = "Churro-Dogo"
        else:
            msg.body("No entendí qué dogo quieres, compa. Escribe: *Sencillo*, *Doble*, *De a Metro* o *Churro-Dogo*.")
            return str(resp)

        estado["paso"] = "esperando_con_todo"
        msg.body(f"¡Bien! Te vamos a preparar un *{estado['tipo_dogo']}*.\n¿Lo quieres *con todo*? 😋\n\n✅ Escribe *sí*\n❌ Escribe *no*")
        return str(resp)

    if estado["paso"] == "esperando_con_todo":
        if "sí" in incoming_msg or "si" in incoming_msg:
            estado["con_todo"] = True
        elif "no" in incoming_msg:
            estado["con_todo"] = False
        else:
            msg.body("Nomás dime si lo quieres *con todo* o *no*, compa. 😅")
            return str(resp)

        estado["paso"] = "esperando_extras"
        msg.body("¿Quieres algo extra de la barra pa’ que amarre? 🍄🧀\n\nEscribe lo que quieras agregar, como:\n- Queso Amarillo\n- Champiñones\n- Tocino\n(Si no quieres nada, escribe *no*)")
        return str(resp)

    if estado["paso"] == "esperando_extras":
        if "no" in incoming_msg:
            estado["extras"] = []
        else:
            # Separa los extras por comas y limpia los espacios en blanco
            extras_list = [
                extra.strip().capitalize()
                for extra in incoming_msg.split(',')
                if extra.strip()
            ]
            estado["extras"] = extras_list

        estado["paso"] = "confirmando"

        resumen = f"📦 *Tu Pedido:*\nSucursal: {estado['sucursal']}\nDogo: {estado['tipo_dogo']}"
        resumen += "\nCon todo: Sí" if estado.get("con_todo") else "\nCon todo: No"
        if estado.get("extras"):
            resumen += f"\nExtras: {', '.join(estado['extras'])}"
        else:
            resumen += "\nExtras: Ninguno"

        resumen += "\n\n¿Le damos pa’ delante? Escribe *sí* pa’ mandar a la plancha 🔥"

        msg.body(resumen)
        return str(resp)

    if estado["paso"] == "confirmando":
        if "sí" in incoming_msg or "si" in incoming_msg:
            msg.body("¡Fierro, compa! Ya se mandó a la plancha tu obra de arte 🔥\nEn unos minutos estará listo. ¡Gracias por tu pedido!")
            del estado_usuarios[user_id]
        else:
            msg.body("Ok, si quieres cambiar algo nomás dime. Si todo está bien, escribe *sí*.")
        return str(resp)

    msg.body("Espérame compa, todavía estoy calentando la plancha 🧠. Próximamente más funciones.")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
