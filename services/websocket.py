from flask_sockets import Sockets
import json

jwt = 'pepe'


def init_websocket(app, uav):
    sockets = Sockets(app)

    @sockets.route('/websocket')
    def websocket(ws):
        while not ws.closed:
            message = ws.receive()
            if message:
                message_data = json.loads(message)
                event = message_data['event']

                match event:
                    case 'authenticate':
                        # check token
                        token = message_data['token']
                        ws.send(json.dumps({'event': 'authenticated'}))

                    case 'battery_check':
                        battery_percent = uav.battery_check()
                        ws.send(json.dumps(
                            {'event': 'battery_check', 'battery_percent': battery_percent}))

                    case 'arm':
                        uav.arm()
                        ws.send(json.dumps({'event': 'armed'}))

                    case 'take_off':
                        uav.take_off()
                        ws.send(json.dumps({'event': 'take_off'}))

                    case 'land':
                        uav.land()
                        ws.send(json.dumps({'event': 'landing'}))

                    case 'shutdown':
                        uav.shutdown()
                        ws.send(json.dumps({'event': 'shutdown'}))

                    case 'reboot':
                        uav.reboot()
                        ws.send(json.dumps({'event': 'reboot'}))

                    case 'status':
                        ws.send(json.dumps(
                            {'event': 'status', 'connected': uav.connected}))
