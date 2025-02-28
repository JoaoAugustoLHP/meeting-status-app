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

# Configuração do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Caminho do arquivo JSON da conta de serviço
CALENDAR_ID = 'cb703793a8843b777f3d4960bc635e3e4ff95a3b36e2fa4d58facd5bbd261c10@group.calendar.google.com'

# Carregar credenciais
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)

def get_calendar_events():
    now = datetime.utcnow().isoformat() + 'Z'  # Tempo atual em formato ISO
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now,
        maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(f"{start}: {event['summary']}")
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
                document.body.style.backgroundColor = '#d4f8d4';
            } else if (status === 'Em Reunião') {
                document.body.style.backgroundColor = '#f5baba';
            } else if (status === 'Externo') {
                document.body.style.backgroundColor = '#e5c100';
            }
        }
        
        window.onload = fetchStatus;
        setInterval(fetchStatus, 3000);
    </script>
</head>
<body>
    <h1 id='status-text'>Status: {{ status['status'] }}</h1>
    <p id='last-updated'>Última atualização: {{ status['last_updated'] }}</p>
    <button class='disponivel' onclick="updateStatus('Disponível')">Disponível 🟢</button>
    <button class='reuniao' onclick="updateStatus('Em Reunião')">Em Reunião 🔴</button>
    <button class='externo' onclick="updateStatus('Externo')">Externo 🟡</button>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, status=status)

@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify(status)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
