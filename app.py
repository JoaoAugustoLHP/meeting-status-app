from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configurações do e-mail
EMAIL_SENDER = "joaoaugusto.lhp1969@gmail.com"
EMAIL_PASSWORD = "dhbi cwnb tueh wmxw"
EMAIL_RECEIVER = "hospitalidade@hospitaldebase.com.br"

# Configuração do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID = 'cb703793a8843b777f3d4960bc635e3e4ff95a3b36e2fa4d58facd5bbd261c10@group.calendar.google.com'

# Carregar credenciais do ambiente ou do arquivo
if os.environ.get("GOOGLE_CREDENTIALS"):
    SERVICE_ACCOUNT_INFO = json.loads(os.environ["GOOGLE_CREDENTIALS"])
else:
    with open("credentials.json") as f:
        SERVICE_ACCOUNT_INFO = json.load(f)

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

def get_calendar_events():
    brt = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(brt).isoformat()
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID, timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
    except Exception as e:
        print(f"Erro ao buscar eventos: {e}")
        events = []
    
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if start:
            try:
                local_time = datetime.fromisoformat(start).astimezone(brt).strftime('%d/%m %H:%M')
                event_list.append(f"<strong>{local_time}</strong> - {event['summary']}")
            except Exception as e:
                print(f"Erro ao converter horário: {e}")
                continue
    return event_list

def send_email(new_status):
    subject = "Atualização de Status"
    brt = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(brt).strftime('%H:%M:%S')
    body = f"O status foi alterado para: {new_status}\nÚltima atualização: {now}"
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

brt = pytz.timezone('America/Sao_Paulo')
status = {"status": "Disponível", "last_updated": datetime.now(brt).strftime('%H:%M:%S')}

@app.route('/')
def home():
    event_list = get_calendar_events()
    print(event_list)  # Debugging
    html_page = """
    <!DOCTYPE html>
    <html lang='pt'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Status da Reunião</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            var socket = io();
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
                });
            }
            function updateBackgroundColor(status) {
                if (status === 'Disponível') {
                    document.body.style.backgroundColor = '#d4f8d4';
                } else if (status === 'Em Reunião') {
                    document.body.style.backgroundColor = '#f5baba';
                } else if (status === 'Externo') {
                    document.body.style.backgroundColor = '#e5c100';
                }
            }
            function toggleAgenda() {
                let container = document.getElementById('eventos-container');
                container.style.display = (container.style.display === 'none' || container.style.display === '') ? 'block' : 'none';
            }
        </script>
    </head>
    <body>
        <h1 id='status-text'>Status: {status}</h1>
        <p id='last-updated'>Última atualização: {last_updated}</p>
        <button onclick="updateStatus('Disponível')">Disponível</button>
        <button onclick="updateStatus('Em Reunião')">Em Reunião</button>
        <button onclick="updateStatus('Externo')">Externo</button>
        <button id="agenda-btn" onclick="toggleAgenda()">Ver Agenda 📅</button>
        <div id='eventos-container' style='display: none;'>
            <h3>Próximas Reuniões:</h3>
            <div>{events}</div>
        </div>
    </body>
    </html>
    """.format(status=status["status"], last_updated=status["last_updated"], events='<br>'.join(event_list))
    return render_template_string(html_page)

@app.route('/update_status', methods=['POST'])
def update_status():
    global status
    new_status = request.json.get("status")
    status["status"] = new_status
    status["last_updated"] = datetime.now(brt).strftime('%H:%M:%S')
    send_email(new_status)
    socketio.emit('status_update', status, namespace='/')
    return jsonify(status)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
