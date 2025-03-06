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

CALENDAR_ID = 'cb703793a8843b777f3d4960bc635e3e4ff95a3b36e2fa4d58facd5bbd261c10@group.calendar.google.com'

def get_calendar_events():
    """Busca os próximos eventos da agenda do Google."""
    try:
        brt = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(brt).isoformat()
        events_result = service.events().list(
            calendarId=CALENDAR_ID, timeMin=now,
            maxResults=5, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            local_time = datetime.fromisoformat(start).astimezone(brt)
            formatted_date = local_time.strftime('%d/%m')
            formatted_time = local_time.strftime('%H:%M')
            event_list.append(f"<b>{formatted_date} - {formatted_time}</b> ➜ {event['summary']}")

        return event_list
    except Exception as e:
        print(f"Erro ao buscar eventos do Google Calendar: {e}")
        return ["Erro ao carregar eventos"]

HTML_PAGE = """
<!DOCTYPE html>
<html lang='pt'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Status da Reunião</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; transition: background-color 0.5s; }
        #eventos-container { display: none; margin-top: 20px; background: white; padding: 10px; border-radius: 8px; }
    </style>
    <script>
        var socket = io.connect('https://' + document.domain + ':' + location.port);

        function atualizarAgenda() {
            fetch('/get_events')
                .then(response => response.json())
                .then(data => {
                    let eventosLista = document.getElementById('eventos-lista');
                    eventosLista.innerHTML = "";
                    data.events.forEach(event => {
                        let item = document.createElement('p');
                        item.innerHTML = event;
                        eventosLista.appendChild(item);
                    });
                });
        }

        function toggleAgenda() {
            let container = document.getElementById('eventos-container');
            if (container.style.display === 'none') {
                atualizarAgenda();
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        }

        setInterval(atualizarAgenda, 30000);  // Atualiza a agenda a cada 30 segundos
    </script>
</head>
<body>
    <h1 id='status-text'>Status: {{ status['status'] }}</h1>
    <p id='last-updated'>Última atualização: {{ status['last_updated'] }}</p>
    <button onclick="toggleAgenda()">Ver Agenda 📅</button>
    <div id="eventos-container">
        <h3>📅 Próximas Reuniões:</h3>
        <div id="eventos-lista"></div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, status=status)

@app.route('/get_events', methods=['GET'])
def get_events():
    return jsonify({'events': get_calendar_events()})

@app.route('/update_status', methods=['POST'])
def update_status():
    try:
        global status
        data = request.json
        status["status"] = data.get("status", status["status"])
        status["last_updated"] = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%H:%M:%S')
        socketio.emit('status_update', status)
        return jsonify(status)
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")
        return jsonify({"error": "Erro ao atualizar status"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
