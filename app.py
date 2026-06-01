from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO

app = Flask(__name__)
# Habilitamos CORS para que Ngrok no bloquee los WebSockets
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================================
# FRONTEND: Página web ultra básica (HTML + JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Prueba GPS Flow</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { 
            font-family: monospace; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            background-color: #222; 
            color: white;
            margin: 0;
        }
        .monitor {
            background: #000;
            padding: 40px;
            border-radius: 10px;
            border: 2px solid #00ff00;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            text-align: center;
        }
        #coords {
            font-size: 3rem;
            color: #00ff00;
            margin-top: 20px;
        }
        .status { color: #888; font-size: 1.2rem; }
    </style>
</head>
<body>
    <div class="monitor">
        <h2>Rastreador de Flujo - Modo Prueba</h2>
        <div class="status" id="status">Conectando al servidor...</div>
        <div id="coords">Esperando coordenadas...</div>
    </div>

    <script>
        // 1. Conectar al servidor Socket.IO local
        const socket = io();

        // 2. Confirmar conexión en pantalla
        socket.on('connect', function() {
            document.getElementById('status').innerText = "🟢 Conectado por WebSocket. Esperando a LILYGO...";
            document.getElementById('status').style.color = "#00ff00";
        });

        // 3. Escuchar el evento 'new_location' (igual que en tu app de Dart)
        socket.on('new_location', function(data) {
            console.log("Recibido:", data);
            const lat = parseFloat(data.lat).toFixed(6);
            const lng = parseFloat(data.lng).toFixed(6);
            
            // Actualizar la pantalla gigante
            document.getElementById('coords').innerHTML = "LAT: " + lat + "<br>LNG: " + lng;
            
            // Efecto de parpadeo para saber que llegó dato nuevo
            document.getElementById('coords').style.color = "white";
            setTimeout(() => { document.getElementById('coords').style.color = "#00ff00"; }, 300);
        });

        socket.on('disconnect', function() {
            document.getElementById('status').innerText = "🔴 Desconectado del servidor.";
            document.getElementById('status').style.color = "red";
        });
    </script>
</body>
</html>
"""

# ==========================================
# RUTAS DEL SERVIDOR
# ==========================================

# Ruta para ver la página web
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/test')
def test():
    print("PETICIÓN RECIBIDA DESDE EL MÓDEM")
    return "OK", 200

@app.route('/prueba', methods=['GET', 'POST'])
def prueba():
    print("Método:", request.method)
    print("Datos:", request.data)
    return "OK", 200



@app.route('/ping', methods=['GET'])
def ping():
    print("PING RECIBIDO")
    return "pong", 200
# Ruta que recibe los datos del ESP32 (LILYGO)
@app.route('/api/update_location', methods=['POST'])
def update_location():
    data = request.get_json()

    print("================================")
    print("DATOS RECIBIDOS DEL LILYGO")
    print(data)
    print("================================")

    socketio.emit('new_location', data)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    print("Iniciando servidor Flask de prueba en el puerto 5000...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)