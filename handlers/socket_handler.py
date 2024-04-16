# handlers/socket_handler.py
import socketio
import traceback

from handlers.pixhawk_handler import pixhawk_handler_msg


async def websocket_connect(uav_instance):
    print(' --> Initiating websocket...')

    sio = socketio.AsyncClient()

    @sio.event
    def connect():
        print(' --> Connecting to socket service...')

    @sio.event
    def authenticateduav(sid):
        print(' --> Authenticated from service.')

    @sio.event
    async def message(msg, socket_recipient_id):
        await pixhawk_handler_msg(msg, socket_recipient_id, sio, uav_instance)

    @sio.event
    def disconnect():
        print('Disconnected from server')
        print('Attempting to reconnect...')
        try:
            sio.connect('https://uav-nextjs.onrender.com/api/socket')
            sio.emit('authenticateuav', ('PajaroLoco', '123'))
        except Exception as e:
            print("Error:", e)
            traceback.print_exc()

    try:
        await sio.connect('https://uav-nextjs.onrender.com/api/socket')
        # await sio.connect('http://192.168.1.12:3000/api/socket')
        await sio.emit('authenticateuav', ('PajaroLoco', '123'))

        # timeoput = 20
        # await asyncio.wait_for(sio.wait(), timeout)

    except Exception as e:
        print(" --> Error:", e)
        # intentar reconexion
        traceback.print_exc()
