# handlers/socket.py
from flask_socketio import SocketIO, emit, disconnect
from threading import Thread
import time


class SocketHandler:
    def __init__(self, socketio):
        self.socketio = socketio
        self.connectedClient = False

    def connect(self, jwt):
        print('Connecting to socket...')
        if self.verifyToken(jwt):
            print('Client connected with token:', jwt)
            self.connectedClient = True
        else:
            print('Client failed to connect with token:', jwt)
            disconnect()

    def disconnect(self):
        self.connectedClient = False

    def receive(self, message):
        if self.connectedClient:
            print('Received:', message)

    def send(self, message):
        self.socketio.emit('message', message)

    def sendStatus(self):
        while self.connectedClient:
            self.socketio.emit('status', {'connected': self.connectedClient})
            time.sleep(10)

    def verifyToken(self, jwt):
        if jwt != '123':
            return False
        return True
