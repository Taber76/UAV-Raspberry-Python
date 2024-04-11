# handlers/pixhawk_handler_msg.py
import json

from controllers.pixhawk_controller import PixhawkController


async def pixhawk_handler_msg(msg, socket_recipient_id, sio, uav_instance):
    try:
        if msg is None:
            return
        json_msg = json.loads(msg)

        if PixhawkController._instance is None:
            uav_instance = PixhawkController()

        if uav_instance.client_socket_id == None:
            uav_instance.client_socket_id = socket_recipient_id
            print("--> UAV connected to client id: " + str(socket_recipient_id))
            await sio.emit('message', ('{"type": "acceptedConnection", "uavpass": "' +
                                       str(uav_instance.uavpass) + '" }', uav_instance.client_socket_id))

        # elif json_msg['uavpass'] != uav_instance.uavpass:
        #    print(json_msg['uavpass'], uav_instance.uavpass)
        #    await sio.emit(
        #        'message', ('{"type": "rejectedConnection"}', socket_recipient_id))

        elif json_msg['type'] == 'disconnectUav':
            print("UAV disconnected. ID: " + str(socket_recipient_id))
            uav_instance.client_socket_id = None

        elif json_msg['type'] == 'heartbeat':
            battery = await uav_instance.battery_check()
            # await uav_instance.get_coordinates()
            coordinates = (-54, -33, 10)
            attitude = await uav_instance.get_attitude()
            values = (battery,) + coordinates + attitude
            keys_ = ["battery", "lat", "lon", "alt", "pitch", "roll", "yaw"]
            response = {key: value for key, value in zip(keys_, values)}
            response["type"] = "stauts"
            await sio.emit('message', (json.dumps(response), uav_instance.client_socket_id))

        elif json_msg['type'] == 'batteryCheck':
            print('TIPO BATERIA')
            response = await uav_instance.battery_check()
            await sio.emit('message', (json.dumps(
                {'type': 'batteryCheck', 'battery_percent': response}), uav_instance.client_socket_id))

        elif json_msg['type'] == 'armUav':
            await uav_instance.arm()

        elif json_msg['type'] == 'takeOffUav':
            await uav_instance.take_off()
    finally:
        pass
