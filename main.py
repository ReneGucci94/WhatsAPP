from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

MENU = {
    "sencillo": {"nombre": "Dogo Sencillo", "precio": 55},
    "doble": {"nombre": "Dogo Doble", "precio": 75},
    "metro": {"nombre": "Dogo de a Metro", "precio": 450},
    "churro": {"nombre": "Churro-Dogo", "precio": 80}
}

INGREDIENTES_BASE = ["frijol", "chorizo", "cebolla con tocino", "lechuga", "tomate", "mayonesa"]
estado_usuarios = {}

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    user_id = request.values.get("From")
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    estado_actual = estado_usuarios.get(user_id)

    if incoming_msg in ["cancelar", "reiniciar", "empezar de nuevo"]:
        if user_id in estado_usuarios:
            del estado_usuarios[user_id]
        msg.body("¡Sale, compa! Pedido cancelado. Empezamos de cero cuando quieras, nomás manda cualquier mensaje.")
        return str(resp)

    if not estado_actual:
        estado_actual = {"paso": "esperando_sucursal", "pedido": {}}
        estado_usuarios[user_id] = estado_actual

    paso_actual = estado_actual.get("paso")

    if paso_actual == "esperando_sucursal":
        # Ignorar saludos sin interrumpir el flujo
        if incoming_msg in ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]:
            msg.body("¿Pa’ qué sucursal va a ser el dogo?\n\n👉 *Jardines*\n👉 *Pueblitos*\n👉 *Puerta Real*")
            return str(resp)

        sucursal_elegida = None
        if "jardines" in incoming_msg:
            sucursal_elegida = "Jardines"
        elif "pueblitos" in incoming_msg:
            sucursal_elegida = "Pueblitos"
        elif "puerta" in incoming_msg:
            sucursal_elegida = "Puerta Real"

        if sucursal_elegida:
            estado_actual["pedido"]["sucursal"] = sucursal_elegida
            estado_actual["paso"] = "esperando_dogo"
            msg.body(f"¡Fierro, pa’ *{sucursal_elegida}*! 🔥 Ahora, ármate el dogo a tu gusto:\n\n🌭 Sencillo\n🌭🌭 Doble\n📏 De a Metro\n🥐 Churro-Dogo")
        else:
            msg.body("No caché bien eso, compa. Escríbeme: *Jardines*, *Pueblitos* o *Puerta Real*.")
        return str(resp)

    if paso_actual == "esperando_dogo":
        # Ignorar saludos comunes sin romper el flujo
        if incoming_msg in ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]:
            sucursal = estado_actual["pedido"].get("sucursal", "")
            msg.body(
                f"¡Fierro, pa’ *{sucursal}*! 🔥 Ahora, ármate el dogo a tu gusto:\n\n"
                "🌭 Sencillo\n🌭🌭 Doble\n📏 De a Metro\n🥐 Churro-Dogo"
            )
            return str(resp)

        tipo_dogo_elegido = None
        for key, value in MENU.items():
            if key in incoming_msg:
                tipo_dogo_elegido = value
                estado_actual["pedido"]["tipo_dogo"] = value
                break

        if tipo_dogo_elegido:
            estado_actual["paso"] = "esperando_con_todo"
            msg.body(f"¡Bien! Un *{tipo_dogo_elegido['nombre']}*.\n¿Lo quieres *con todo*? 😋\n\n(Lleva: {', '.join(INGREDIENTES_BASE)})\n\n✅ Escribe *sí*\n❌ Escribe *no*")
        else:
            msg.body("No entendí qué dogo quieres, compa. Escribe: *Sencillo*, *Doble*, *De a Metro* o *Churro-Dogo*.")
        return str(resp)

    if paso_actual == "esperando_con_todo":
        # Ignorar saludos comunes sin romper el flujo
        if incoming_msg in ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]:
            tipo = estado_actual["pedido"].get("tipo_dogo", {}).get("nombre", "")
            msg.body(
                f"¡Bien! Un *{tipo}*.\n¿Lo quieres *con todo*? 😋\n\n(Lleva: {', '.join(INGREDIENTES_BASE)})\n\n✅ Escribe *sí*\n❌ Escribe *no*"
            )
            return str(resp)

        if incoming_msg.startswith("sin"):
            estado_actual["pedido"]["con_todo"] = False
            exclusiones = [item.strip() for item in incoming_msg.replace("sin", "").split(",")]
            estado_actual["pedido"]["exclusiones"] = exclusiones
            estado_actual["paso"] = "esperando_extras"
            msg.body("¡Anotado, compa! Ya no le echamos eso. ¿Quieres algo extra de la barra? 🍄🧀\n\n(Si no quieres nada, escribe *no*)")
        elif incoming_msg in ["no"]:
            estado_actual["pedido"]["con_todo"] = False
            estado_actual["paso"] = "esperando_exclusiones"
            msg.body(f"¡Entendido! Sin todo. ¿Hay algo en específico que **NO** le ponemos?\n\n(Ej: *cebolla, tomate*)")
        elif incoming_msg in ["sí", "si"]:
            estado_actual["pedido"]["con_todo"] = True
            estado_actual["paso"] = "esperando_extras"
            msg.body("¡Perfecto! ¿Quieres algo extra de la barra pa’ que amarre? 🍄🧀\n\n(Si no quieres nada, escribe *no*)")
        else:
            msg.body("Nomás dime si lo quieres *con todo*, *no* o *sin* algún ingrediente específico 😅")
        return str(resp)

    if paso_actual == "esperando_exclusiones":
        # Ignorar saludos comunes sin romper el flujo
        if incoming_msg in ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]:
            msg.body("¡Entendido! Sin todo. ¿Hay algo en específico que **NO** le ponemos?\n\n(Ej: *cebolla, tomate*)")
            return str(resp)

        exclusiones = [item.strip() for item in incoming_msg.split(',')]
        estado_actual["pedido"]["exclusiones"] = exclusiones
        estado_actual["paso"] = "esperando_extras"
        msg.body("Anotado. ¿Y quieres agregar algo extra de la barra? 🍄🧀\n\n(Si no quieres agregar nada, escribe *no*)")
        return str(resp)

    if paso_actual == "esperando_extras":
        # Ignorar saludos comunes sin romper el flujo
        if incoming_msg in ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]:
            msg.body("¿Quieres algo extra de la barra? 🍄🧀\n\n(Si no quieres nada, escribe *no*)")
            return str(resp)

        if "no" in incoming_msg:
            estado_actual["pedido"]["extras"] = []
        else:
            extras = [item.strip().capitalize() for item in incoming_msg.split(',')]
            estado_actual["pedido"]["extras"] = extras

        estado_actual["paso"] = "confirmando"

        pedido = estado_actual['pedido']
        total = pedido['tipo_dogo']['precio']

        resumen = f"📦 *Revisa tu Pedido:*\n"
        resumen += f"Sucursal: *{pedido['sucursal']}*\n"
        resumen += f"Dogo: *{pedido['tipo_dogo']['nombre']}* (${pedido['tipo_dogo']['precio']})\n"

        if pedido.get("con_todo") is True:
            resumen += "Con todo: *Sí*\n"
        elif pedido.get("exclusiones"):
            resumen += f"Sin: *{', '.join(pedido['exclusiones'])}*\n"
        else:
            resumen += "Con todo: *No especificado*\n"

        if pedido.get("extras"):
            resumen += f"Extras: *{', '.join(pedido['extras'])}*\n"

        resumen += f"\n*Total a Pagar (Estimado): ${total} MXN*\n\n"
        resumen += "¿Le damos pa’ delante? Escribe *sí* pa’ mandar a la plancha 🔥"
        msg.body(resumen)
        return str(resp)

    if paso_actual == "confirmando":
        # Ignorar saludos comunes sin romper el flujo
        if incoming_msg in ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches"]:
            pedido = estado_actual["pedido"]
            total = pedido["tipo_dogo"]["precio"]
            resumen = f"📦 *Revisa tu Pedido:*\n"
            resumen += f"Sucursal: *{pedido['sucursal']}*\n"
            resumen += f"Dogo: *{pedido['tipo_dogo']['nombre']}* (${pedido['tipo_dogo']['precio']})\n"
            if pedido.get("con_todo") is True:
                resumen += "Con todo: *Sí*\n"
            elif pedido.get("exclusiones"):
                resumen += f"Sin: *{', '.join(pedido['exclusiones'])}*\n"
            else:
                resumen += "Con todo: *No especificado*\n"
            if pedido.get("extras"):
                resumen += f"Extras: *{', '.join(pedido['extras'])}*\n"
            resumen += f"\n*Total a Pagar (Estimado): ${total} MXN*\n\n"
            resumen += "¿Le damos pa’ delante? Escribe *sí* pa’ mandar a la plancha 🔥"
            msg.body(resumen)
            return str(resp)

        if "sí" in incoming_msg or "si" in incoming_msg:
            msg.body("¡Fierro, compa! Ya se mandó a la plancha tu obra de arte 🔥\nTu pedido #103 estará listo en 20 mins. ¡Gracias por tu pedido!")
            del estado_usuarios[user_id]
        else:
            msg.body("Ok, pedido no confirmado. Escribe *cancelar* para empezar de nuevo o *sí* para confirmar.")
        return str(resp)

    msg.body("No te entendí, compa. Si quieres empezar de nuevo, escribe *cancelar*.")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
# Versión refinada 2.1 con resumen de exclusiones corregido
