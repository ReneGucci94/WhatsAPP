from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os, json

app = Flask(__name__)

MENU = {
    "sencillo": {"nombre": "Dogo Sencillo", "precio": 55},
    "doble": {"nombre": "Dogo Doble", "precio": 75},
    "metro": {"nombre": "Dogo de a Metro", "precio": 450},
    "churro": {"nombre": "Churro-Dogo", "precio": 80}
}
INGREDIENTES_BASE = ["frijol", "chorizo", "cebolla con tocino", "lechuga", "tomate", "mayonesa"]

def guardar_estado(user_id, estado):
    if not os.path.exists("estados"):
        os.makedirs("estados")
    with open(f"estados/{user_id}.json", "w") as f:
        json.dump(estado, f)

def cargar_estado(user_id):
    try:
        with open(f"estados/{user_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def borrar_estado(user_id):
    try:
        os.remove(f"estados/{user_id}.json")
    except FileNotFoundError:
        pass

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    user_id = request.values.get("From")
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    estado_actual = cargar_estado(user_id)

    if incoming_msg in ["cancelar", "reiniciar", "empezar de nuevo"]:
        borrar_estado(user_id)
        msg.body("¡Sale, compa! Pedido cancelado. Empezamos de cero cuando quieras, nomás manda cualquier mensaje.")
        return str(resp)

    if not estado_actual:
        estado_actual = {"paso": "esperando_sucursal", "pedido": {}}
        msg.body("¡Qué onda, compa! Bienvenido a *Dogos El Compadre* 🌭🔥\n¿Pa’ qué sucursal va a ser el dogo?\n\n👉 *Jardines*\n👉 *Pueblitos*\n👉 *Puerta Real*")
        guardar_estado(user_id, estado_actual)
        return str(resp)

    paso_actual = estado_actual.get("paso")

    if paso_actual == "esperando_sucursal":
        sucursal = None
        if "jardines" in incoming_msg: sucursal = "Jardines"
        elif "pueblitos" in incoming_msg: sucursal = "Pueblitos"
        elif "puerta" in incoming_msg: sucursal = "Puerta Real"

        if sucursal:
            estado_actual["pedido"]["sucursal"] = sucursal
            estado_actual["paso"] = "esperando_dogo"
            msg.body(f"¡Fierro, pa’ *{sucursal}*! 🔥 Ahora, ármate el dogo a tu gusto:\n\n🌭 Sencillo\n🌭 Doble\n📏 De a Metro\n🥐 Churro-Dogo")
        else:
            msg.body("No caché bien eso, compa. Escríbeme: *Jardines*, *Pueblitos* o *Puerta Real*.")

        guardar_estado(user_id, estado_actual)
        return str(resp)

    if paso_actual == "esperando_dogo":
        tipo = incoming_msg
        if tipo in MENU:
            estado_actual["pedido"]["tipo_dogo"] = MENU[tipo]
            estado_actual["paso"] = "esperando_con_todo"
            msg.body(f"¡Bien! Un *{MENU[tipo]['nombre']}*.\n¿Lo quieres *con todo*? 😋\n\n(Lleva: {', '.join(INGREDIENTES_BASE)})\n\n✅ Escribe *sí*\n❌ Escribe *no* o *sin*...")
        else:
            msg.body("No entendí qué dogo quieres, compa. Escribe una sola opción: *Sencillo*, *Doble*, *Metro* o *Churro*.")

        guardar_estado(user_id, estado_actual)
        return str(resp)

    msg.body("Me perdí, compa. Si quieres empezar de nuevo, escribe *cancelar*.")
    return str(resp)
