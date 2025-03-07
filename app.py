import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO
import os
import json
from datetime import datetime
import pytz
from googleapiclient.discovery import build
from google.oauth2 import service_account
from eventlet.green import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

status = {"status": "Disponível", "last_updated": "00:00:00"}

# Configuração do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")

if not GOOGLE_CREDENTIALS:
    raise ValueError("Erro: Variável de ambiente GOOGLE_CREDENTIALS não encontrada.")

try:
    SERVICE_ACCOUNT_INFO = json.loads(GOOGLE_CREDENTIALS)
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
except Exception as e:
    raise ValueError(f"Erro ao carregar credenciais do Google: {e}")

# Lista de IDs das agendas
CALENDAR_IDS = [
    "hospitalidadeandreza@gmail.com",
    "1f74d46732f963419be353393a709bc66abc1f731a0d712c228d6a77f6c80cae@group.calendar.google.com",
    "5d2857d77cafddff7856b95aa55a7cf78f5f21aa3bae01cfe15f9d9385f6bf33@group.calendar.google.com",
    "8bb38e2ac53dc483599c87f9a07b1c8e48fc8900b97aae0a100c17e7bfd1203e@group.calendar.google.com",
    "cb703793a8843b777f3d4960bc635e3e4ff95a3b36e2fa4d58facd5bbd261c10@group.calendar.google.com"
]

# Criando um lock para evitar múltiplas leituras simultâneas
lock = threading.Lock()

def get_calendar_events():
    """Busca os próximos eventos de todas as agendas do Google."""
    global service
    with lock:
        try:
            brt = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(brt).isoformat()

            event_list = []
            for calendar_id in CALENDAR_IDS:
                events_result = service.events().list(
                    calendarId=calendar_id, timeMin=now,
                    maxResults=5, singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    local_time = datetime.fromisoformat(start).astimezone(brt)
                    formatted_date = local_time.strftime('%d/%m')
                    formatted_time = local_time.strftime('%H:%M')
                    event_list.append(f"<b>{formatted_date} - {formatted_time}</b> ➜ {event['summary']}")

            event_list.sort()
            return event_list[:10]
        except Exception as e:
            print(f"Erro ao buscar eventos do Google Calendar: {e}")
            return ["Erro ao carregar eventos"]

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, status=status)

@app.route('/get_events', methods=['GET'])
def get_events():
    return jsonify({'events': get_calendar_events()})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
