# connections/socket_connection.py
from flask import Flask, jsonify
import requests


def send_beat_socket():
    login_url = 'https://uav-nextjs.onrender.com/api/uav/login'
    socket_url = 'https://uav-nextjs.onrender.com/api/socket'
    # url = 'https://uav-cloud-server.vercel.app/api/uav/uavconnect'
    # url = 'http://localhost:3000/api/uav/uavconnect'
    data = {
        'uavname': 'PajaroLoco',
        'password': '123',
        'jwt': '123'
    }

    try:
        response = requests.post(login_url, json=data)
        if response.status_code == 200:
            requests.get(socket_url)
            return True

    except requests.exceptions.RequestException as e:
        return False
