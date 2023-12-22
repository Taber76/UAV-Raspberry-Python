# main.py

# Librerias server
import time
from flask import Flask
from flask_socketio import SocketIO

from connections.cloud_connection import send_post_cloud
from handlers.socket_handler import SocketHandler
from handlers import event_handler


# SERVER ------------------------------------------------------------
# comprobar conexion a internet

# comunicarse con servidor en la nube y obeter autorizacion
print('Connecting to cloud...')
response = False

while not response:
    response = send_post_cloud()
    if not response:
        print('Connection to cloud failed. Retrying in 5 seconds...')
        time.sleep(5)

print('Connected to cloud successfully!')

# configura el servidor Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
socket_handler = SocketHandler(socketio)

# registra los manejadores de eventos
event_handler.register_handlers(socketio, socket_handler)


# inicia el servidor
if __name__ == '__main__':
    # socket_handler.sendStatus()
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
