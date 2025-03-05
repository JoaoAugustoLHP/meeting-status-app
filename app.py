from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

status = "Disponível"

# Carregar credenciais do Google corretamente
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

@app.route('/')
def index():
    return "Meeting Status App is running!"

@app.route('/update_status', methods=['POST'])
def update_status():
    global status
    data = request.json
    status = data.get('status', status)
    socketio.emit('status_update', {'status': status}, broadcast=True)
    return jsonify({'message': 'Status atualizado com sucesso!', 'status': status})

@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify({'status': status})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
