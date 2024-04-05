# handlers/socket.py
import socketio
import traceback

from handlers.pixhawk import pixhawk_handler_msg


def websocket_connect():
    print(' Initiating websocket...')

    sio = socketio.Client()

    @sio.event
    def connect():
        print(' Connecting to socket service...')

    @sio.event
    def authenticateduav(sid):
        print(' Authenticated from service.')

    @sio.event
    def message(msg, socket_recipient_id):
        pixhawk_handler_msg(msg, socket_recipient_id, sio)

    try:
        sio.connect('https://uav-nextjs.onrender.com/api/socket')
        sio.emit('authenticateuav', ('PajaroLoco', '123'))
        sio.wait()

    except Exception as e:
        print("Error:", e)
        # intentar reconexion
        traceback.print_exc()
