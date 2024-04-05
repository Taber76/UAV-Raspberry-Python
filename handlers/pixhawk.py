# handlers/pixhawk.py
import random
import json

from connections.pixhawk import PixhawkController

uav = PixhawkController
uavpass = random.randint(10**9, 10**10 - 1)


async def pixhawk_handler_msg(msg, socket_recipient_id, sio):
    json_msg = json.loads(msg)

    if PixhawkController.client_socket_id == None:
        PixhawkController.client_socket_id = socket_recipient_id
        print("UAV connected. ID: " + str(socket_recipient_id))
        sio.emit('message', ('{"type": "acceptedConnection", "uavpass": "' +
                 str(uavpass) + '" }', socket_recipient_id))

    elif json_msg['uavpass'] != uavpass:
        sio.emit(
            'message', ('{"type": "rejectedConnection"}', socket_recipient_id))

    elif json_msg['type'] == 'disconnectUav':
        print("UAV disconnected. ID: " + str(socket_recipient_id))
        PixhawkController.client_socket_id = None

    elif json_msg['type'] == 'batteryCheck':
        response = await uav.battery_check()
        sio.emit('message', (json.dumps(
            {'type': 'batteryCheck', 'battery_percent': response}), socket_recipient_id))

    elif json_msg['type'] == 'armUav':
        await uav.arm()

    elif json_msg['type'] == 'takeOffUav':
        await uav.take_off()
