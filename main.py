import os
import requests
import json
import datetime
import sqlite3
from dotenv import load_dotenv # Importa esto

load_dotenv() # Llama a esta función al inicio para cargar las variables del .env


#me conecto con la base de datos 
conn=sqlite3.connect('data.db')
c=conn.cursor()
c.execute("""SELECT cuentas.cod_cue, ventas.cod_ven, clientes.nom_cont,plataformas.nom_pla,
CAST(julianday(cuentas.fec_cul) - julianday(DATE('now')) AS INTEGER) AS dias_restantes, 
cuentas.fec_cul
FROM cuentas, ventas,clientes, plataformas WHERE dias_restantes IN (20) 
and cuentas.cod_ven=ventas.cod_ven 
and clientes.id=ventas.cod_cli
and plataformas.cod_pla=cuentas.cod_pla
ORDER BY dias_restantes ASC, fec_cul ASC;""")

imp=c.fetchall()


def enviar_mensaje_telegram(cuenta):
    """Envía un mensaje a un chat de Telegram."""
    mensaje=f"Mensaje para {cuenta[2]}. \n \nHola solo queria hacerte recordar que tu suscripción a {cuenta[3]} esta próximo a vencer. No te quedes sin disfrutar lo mejor de contenido Premium. La suscripción vencerá el {cuenta[5]}. Gracias."
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Las variables de entorno de Telegram no están configuradas.")
        # Si estás en desarrollo, puedes agregar esto para ver las variables:
        print(f"Token: {TELEGRAM_BOT_TOKEN}")
        print(f"Chat ID: {TELEGRAM_CHAT_ID}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown" # Opcional: para usar formato Markdown
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Lanza una excepción si la respuesta no es exitosa (código 4xx o 5xx)
        print(f"Mensaje enviado a Telegram: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR al enviar mensaje a Telegram: {e}")
        print(f"Respuesta del servidor: {response.text if 'response' in locals() else 'No hay respuesta'}")


def ejecutar_tarea_diaria():
    """Aquí colocas la lógica de tu tarea diaria."""
    print(f"Ejecutando tarea diaria a las {datetime.datetime.now()}...")

    # --- SIMULACIÓN DE RESULTADOS ---

    if imp:
        for fila, cuenta in enumerate(imp):
            enviar_mensaje_telegram(cuenta)
    

if __name__ == "__main__":
    ejecutar_tarea_diaria()

conn.commit()
conn.close()