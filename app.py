import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string, jsonify, request, send_from_directory
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

# ID da Agenda do Google (substitua pelo seu)
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

            # Melhorando a formatação para facilitar a leitura
            event_list.append(f"<b>{formatted_date} - {formatted_time}</b> ➜ {event['summary']}")

        return event_list

    except Exception as e:
        print(f"Erro ao buscar eventos do Google Calendar: {e}")
        return ["Erro ao carregar eventos"]

# Página HTML com WebSocket e integração com Google Agenda
HTML_PAGE = """
<!DOCTYPE html>
<html lang='pt'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Status da Reunião</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; transition: background-color 0.5s; }
        h1 { color: #333; }
        button { font-size: 18px; padding: 10px 20px; margin: 10px; cursor: pointer; border: none; border-radius: 5px; }
        .disponivel { background-color: green; color: white; }
        .reuniao { background-color: red; color: white; }
        .externo { background-color: orange; color: white; }
        #eventos-container { display: none; margin-top: 20px; background: white; padding: 10px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        #toggle-agenda { margin-top: 20px; background-color: blue; color: white; }
        #eventos-lista p { font-size: 16px; margin: 5px 0; line-height: 1.5; }
    </style>
    <script>
        var socket = io.connect('https://' + document.domain + ':' + location.port);

        socket.on('status_update', function(data) {
            document.getElementById('status-text').innerText = 'Status: ' + data.status;
            document.getElementById('last-updated').innerText = 'Última atualização: ' + data.last_updated;
            updateBackgroundColor(data.status);
        });

        function updateStatus(newStatus) {
            fetch('/update_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'status': newStatus })
            }).then(response => response.json())
              .then(data => {
                  document.getElementById('status-text').innerText = 'Status: ' + data.status;
                  document.getElementById('last-updated').innerText = 'Última atualização: ' + data.last_updated;
                  updateBackgroundColor(data.status);
              });
        }

        function updateBackgroundColor(status) {
            if (status === 'Disponível') {
                document.body.style.backgroundColor = '#d4f8d4'; // Verde claro
            } else if (status === 'Em Reunião') {
                document.body.style.backgroundColor = '#f5baba'; // Vermelho mais forte
            } else if (status === 'Externo') {
                document.body.style.backgroundColor = '#e5c100'; // Amarelo mais escuro
            }
        }

        function toggleAgenda() {
            let container = document.getElementById('eventos-container');
            if (container.style.display === 'none') {
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
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        }

        setInterval(() => {
            fetch('/get_status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status-text').innerText = 'Status: ' + data.status;
                    document.getElementById('last-updated').innerText = 'Última atualização: ' + data.last_updated;
                    updateBackgroundColor(data.status);
                });
        }, 3000);
    </script>
</head>
<body onload="updateBackgroundColor('{{ status['status'] }}')">
    <h1 id='status-text'>Status: {{ status['status'] }}</h1>
    <p id='last-updated'>Última atualização: {{ status['last_updated'] }}</p>
    <button class='disponivel' onclick="updateStatus('Disponível')">Disponível 🟢</button>
    <button class='reuniao' onclick="updateStatus('Em Reunião')">Em Reunião 🔴</button>
    <button class='externo' onclick="updateStatus('Externo')">Externo 🟡</button>
    <br>
    <button id="toggle-agenda" onclick="toggleAgenda()">Ver Agenda 📅</button>
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
