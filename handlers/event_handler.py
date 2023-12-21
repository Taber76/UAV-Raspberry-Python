# event_handler.py
from flask import Flask, request
from flask_socketio import send, emit


def register_handlers(socketio, socket_handler):
    @socketio.on('connect')
    def handle_connect():
        token = request.args.get('token')
        socket_handler.connect(token)

    @socketio.on('disconnect')
    def handle_disconnect():
        socket_handler.disconnect()

    @socketio.on('message')
    def handle_message(data):
        socket_handler.receive(data)
