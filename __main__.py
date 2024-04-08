# __main__.py

# Server libraries
import time
import sys
import signal
import threading
import asyncio

# Modules
from connections.socket_connection import send_beat_socket
from connections.pixhawk_connection import PixhawkController
from handlers.socket_handler import websocket_connect


# Check internet connection
print('1. Checking internet connection...')

# Connect to pixhawk
print('2. Connecting to Pixhawk...')
# uav_instance =PixhawkController()
# uav_instance.connect()


# Connect to socket
print('3. Connecting to socket...')
response = False
while not response:
    response = send_beat_socket()
    if not response:
        print(' Connection to socket failed. Retrying in 5 seconds...')
        time.sleep(5)


# Main
def signal_handler(sig, frame):
    print('Exiting...')
    # thread.join(timeout=1)
    # thread._stop()
    # sys.exit(0)


if __name__ == '__main__':
    # signal.signal(signal.SIGINT, signal_handler)
    # thread = threading.Thread(target=websocket_connect)
    # thread.start()

    asyncio.run(websocket_connect())

    while True:
        time.sleep(1)
