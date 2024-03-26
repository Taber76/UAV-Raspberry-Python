# main.py

# Server libraries
import time
import asyncio
from flask import Flask

from services.websocket import init_websocket
from connections.cloud import send_post_cloud
from connections.pixhawk import PixhawkController


async def setup():
    # Check internet connection

    # Connect to cloud
    print('1. Connecting to cloud...')
    response = False
    while not response:
        response = send_post_cloud()
        if not response:
            print(' Connection to cloud failed. Retrying in 5 seconds...')
            time.sleep(5)
    print(' Connected to cloud successfully!')

    # Connect to pixhawk
    print('2. Connecting to Pixhawk...')
    uav = PixhawkController()
    await uav.connect()

    # Return uav, thermal
    return uav


# Flask config
app = Flask(__name__)

# routes

# socket
uav = asyncio.run(setup())
init_websocket(app, uav)


# launch server
if __name__ == '__main__':
    import os
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    port = int(os.environ.get('PORT', 8080))
    server = pywsgi.WSGIServer(
        ('0.0.0.0', port), app, handler_class=WebSocketHandler)
    print("== Server online ==")
    server.serve_forever()
