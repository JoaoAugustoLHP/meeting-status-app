from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import pytz  # Certifique-se de que 'pytz' está instalado

app = Flask(__name__)

# Definição do fuso horário correto
fuso_brasilia = pytz.timezone("America/Sao_Paulo")

# Armazena o status globalmente
status = {"status": "Disponível", "last_updated": datetime.now(fuso_brasilia).strftime('%H:%M:%S')}

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
                document.body.style.backgroundColor = '#fce5b8'; // Amarelo claro
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
    status["last_updated"] = datetime.now(fuso_brasilia).strftime('%H:%M:%S')
    return jsonify(status)

@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify(status)

if __name__ == '__main__':
    import os

    port = int(os.environ.get("PORT", 5000))  # Pega a porta do ambiente ou usa 5000 como padrão
    app.run(debug=True, host='0.0.0.0', port=port)
