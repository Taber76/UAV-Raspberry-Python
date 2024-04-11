# __main__.py

# Server libraries
import time
import asyncio

# Modules
from connections.socket_connection import send_beat_socket
from controllers.pixhawk_controller import PixhawkController
from handlers.socket_handler import websocket_connect


async def main():
    # Check internet connection
    print('1. Checking internet connection...')

    # Connect to pixhawk
    print('2. Connecting to Pixhawk...')
    uav_instance = PixhawkController()
    await uav_instance.connect()  # Esperar la conexión al Pixhawk

    # Connect to socket
    print('3. Connecting to socket...')
    response = False
    while not response:
        response = send_beat_socket()
        if not response:
            print(' Connection to socket failed. Retrying in 5 seconds...')
            time.sleep(5)
    await websocket_connect(uav_instance)

    # Main loop
    while True:
        time.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
