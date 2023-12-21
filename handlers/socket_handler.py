from flask_socketio import SocketIO, emit
from threading import Thread
import time


class SocketHandler:
    def __init__(self, socketio):
        self.socketio = socketio
        self.connectedClient = False

    def connect(self, jwt):
        if self.verifyToken(jwt):
            self.connectedClient = True

    def disconnect(self):
        self.connectedClient = False

    def receive(self, message):
        if self.connectedClient:
            self.socketio.emit('message', message)

    def send(self, message):
        self.socketio.emit('message', message)

    def sendStatus(self, status):
        while self.connectedClient:
            self.socketio.emit('status', status)
            time.sleep(10)

    def verifyToken(self, jwt):
        return True
