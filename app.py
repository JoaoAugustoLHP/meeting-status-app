from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import google.auth
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)

# Configurações do e-mail
EMAIL_SENDER = "joaoaugusto.lhp1969@gmail.com"  # Substituir pelo seu e-mail
EMAIL_PASSWORD = "dhbi cwnb tueh wmxw"  # Substituir pela senha do e-mail (usar senha de app no Gmail)
EMAIL_RECEIVER = "hospitalidade@hospitaldebase.com.br"  # E-mail que receberá a notificação

import json

# Configuração do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_INFO = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))  # Carrega as credenciais do ambiente
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
CALENDAR_ID = 'cb703793a8843b777f3d4960bc635e3e4ff95a3b36e2fa4d58facd5bbd261c10@group.calendar.google.com'  # Substituir pelo ID da agenda


# Carregar credenciais
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

def get_calendar_events():
    brt = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(brt).isoformat()  # Tempo atual em formato ISO
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now,
        maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        local_time = datetime.fromisoformat(start).astimezone(brt).strftime('%d/%m %H:%M')
        event_list.append(f"{local_time}: {event['summary']}")
    
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

# Armazena o status globalmente
brt = pytz.timezone('America/Sao_Paulo')
status = {"status": "Disponível", "last_updated": datetime.now(brt).strftime('%H:%M:%S')}

HTML_PAGE = """
<!DOCTYPE html>
<html lang='pt'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Status da Reunião</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; transition: background-color 0.5s; }
        h1 { color: #333; }
        button { font-size: 18px; padding: 10px 20px; margin: 10px; cursor: pointer; border: none; border-radius: 5px; }
        .disponivel { background-color: green; color: white; }
        .reuniao { background-color: red; color: white; }
        .externo { background-color: orange; color: white; }
        #eventos-container { display: none; margin-top: 20px; background: white; padding: 10px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        #toggle-agenda { margin-top: 20px; background-color: blue; color: white; }
    </style>
    <script>
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
        
        function fetchStatus() {
            fetch('/get_status')
                .then(response => response.json())
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
                            item.textContent = event;
                            eventosLista.appendChild(item);
                        });
                    });
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        }

        setInterval(fetchStatus, 3000); // Atualiza o status a cada 3 segundos
    </script>
</head>
<body onload="fetchStatus()">
    <h1 id='status-text'>Status: {{ status['status'] }}</h1>
    <p id='last-updated'>Última atualização: {{ status['last_updated'] }}</p>
    <button class='disponivel' onclick="updateStatus('Disponível')">Disponível 🟢</button>
    <button class='reuniao' onclick="updateStatus('Em Reunião')">Em Reunião 🔴</button>
    <button class='externo' onclick="updateStatus('Externo')">Externo 🟡</button>
    <br>
    <button id="toggle-agenda" onclick="toggleAgenda()">Ver Agenda 📅</button>
    <div id="eventos-container">
        <h3>Próximas Reuniões:</h3>
        <div id="eventos-lista"></div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, status=status)

@app.route('/update_status', methods=['POST'])
def update_status():
    global status
    new_status = request.json.get("status")
    status["status"] = new_status
    status["last_updated"] = datetime.now(brt).strftime('%H:%M:%S')
    send_email(new_status)
    return jsonify(status)

@app.route('/get_events', methods=['GET'])
def get_events():
    return jsonify({'events': get_calendar_events()})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
