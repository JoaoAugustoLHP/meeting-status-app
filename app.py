from flask import Flask, request, jsonify, render_template_string
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
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now,
        maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        local_time = datetime.fromisoformat(start).astimezone(brt).strftime('%d/%m/%Y %H:%M')
        event_list.append(f"{local_time} - {event['summary']}")
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

@app.route('/get_events', methods=['GET'])
def get_events():
    return jsonify({'events': get_calendar_events()})
