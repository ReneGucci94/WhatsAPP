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
    try:
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
    
        # PASO 3: Esperando si lo quiere "con todo"
        if paso_actual == "esperando_con_todo":
            if incoming_msg.startswith("sin"):
                estado_actual["pedido"]["con_todo"] = False
                exclusiones = [item.strip() for item in incoming_msg.replace("sin", "").split(',') if item.strip()]
                estado_actual["pedido"]["exclusiones"] = exclusiones
                estado_actual["paso"] = "esperando_extras"
                msg.body("¡Anotado, compa! No le echamos eso. ¿Quieres algo extra de la barra pa' que amarre? 🍄🧀\n\n(Si no quieres nada, escribe *no*)")
            elif "no" in incoming_msg:
                estado_actual["pedido"]["con_todo"] = False
                estado_actual["paso"] = "esperando_exclusiones"
                msg.body("¡Entendido! ¿Hay algo en específico que **NO** le ponemos?\n\n(Ej: *cebolla, tomate*)")
            elif "sí" in incoming_msg or "si" in incoming_msg:
                estado_actual["pedido"]["con_todo"] = True
                estado_actual["paso"] = "esperando_extras"
                msg.body("¡Perfecto! ¿Quieres algo extra de la barra pa’ que amarre? 🍄🧀\n\n(Si no quieres nada, escribe *no*)")
            else:
                msg.body("Nomás dime *sí*, *no* o *sin* algo, compa 😅")
            guardar_estado(user_id, estado_actual)
            return str(resp)
    
        # PASO 3.5: Exclusiones si dijo "no"
        if paso_actual == "esperando_exclusiones":
            exclusiones = [item.strip() for item in incoming_msg.split(',') if item.strip()]
            estado_actual["pedido"]["exclusiones"] = exclusiones
            estado_actual["paso"] = "esperando_extras"
            msg.body("Anotado. ¿Y quieres agregar algo extra de la barra? 🍄🧀\n\n(Si no quieres agregar nada, escribe *no*)")
            guardar_estado(user_id, estado_actual)
            return str(resp)
    
        # PASO 4: Esperando extras
        if paso_actual == "esperando_extras":
            if incoming_msg == "no":
                estado_actual["pedido"]["extras"] = []
            else:
                extras = [item.strip().capitalize() for item in incoming_msg.split(',') if item.strip()]
                estado_actual["pedido"]["extras"] = extras
    
            estado_actual["paso"] = "confirmando"
            pedido = estado_actual["pedido"]
            total = pedido["tipo_dogo"]["precio"]
    
            resumen = f"📦 *Revisa tu Pedido Final:*\n\n"
            resumen += f"📍 Sucursal: *{pedido['sucursal']}*\n"
            resumen += f"🌭 Dogo: *{pedido['tipo_dogo']['nombre']}* (${total})\n"
    
            if pedido.get("con_todo"):
                resumen += "✅ Con todo: *Sí*\n"
            elif pedido.get("exclusiones"):
                resumen += f"❌ Sin: *{', '.join(pedido.get('exclusiones', []))}*\n"
    
            if pedido.get("extras"):
                resumen += f"➕ Extras: *{', '.join(pedido['extras'])}*\n"
    
            resumen += f"\n*Total a Pagar (Estimado): ${total} MXN*\n\n¿Le damos pa’ delante? Escribe *sí* para confirmar 🔥"
            msg.body(resumen)
            guardar_estado(user_id, estado_actual)
            return str(resp)
    
        # PASO 5: Confirmación final
        if paso_actual == "confirmando":
            if "sí" in incoming_msg or "si" in incoming_msg:
                msg.body("¡Fierro, compa! Ya se mandó a la plancha tu obra de arte 🔥\nTu pedido #104 estará listo en 20 mins. ¡Gracias por tu pedido!")
                borrar_estado(user_id)
            else:
                msg.body("Ok, pedido no confirmado. Escribe *cancelar* para empezar de nuevo o *sí* para confirmar tu orden.")
            return str(resp)
    
        msg.body("Me perdí, compa. Si quieres empezar de nuevo, escribe *cancelar*.")
        return str(resp)
    except Exception as e:
        print(f"[ERROR EN WEBHOOK] {str(e)}")
        resp = MessagingResponse()
        resp.message("Tuvimos un error interno, compa. Intenta otra vez o manda *cancelar*.")
        return str(resp)
