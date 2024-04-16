# __main__.py

# Server libraries
import time
import asyncio

# Modules
from connections.socket_connection import send_beat_socket
from controllers.pixhawk_controller import PixhawkController
from handlers.socket_handler import websocket_connect


async def task_200ms(uav_instance):
    while True:
        await uav_instance.update_task_500ms()
        await asyncio.sleep(0.2)


async def task_5000ms(uav_instance):
    while True:
        await uav_instance.update_task_5000ms()
        await asyncio.sleep(5)


async def start():
    global uav_instance

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

    return True


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start_completed = loop.run_until_complete(start())
    if start_completed:
        loop.create_task(task_200ms(uav_instance))
        loop.create_task(task_5000ms(uav_instance))
        loop.run_forever()
