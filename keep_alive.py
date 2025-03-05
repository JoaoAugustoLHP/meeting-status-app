import requests
import time

url = "https://meeting-status-app.onrender.com"

while True:
    try:
        response = requests.get(url)
        print(f"Ping enviado! Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
    
    time.sleep(600)  # Espera 10 minutos antes de enviar outro ping
