from flask import Flask, jsonify
import requests


def send_post_cloud():
    # url = 'https://uav.vercel.app/api/uav/uavconnect'
    url = 'https://uav-cloud-server.vercel.app/api/uav/uavconnect'
    # url = 'http://localhost:3000/api/uav/uavconnect'
    data = {
        'uavname': 'PajaroLoco',
        'password': '123',
        'jwt': '123'
    }

    try:
        response = requests.post(url, json=data).json()
        return response['response']

    except requests.exceptions.RequestException as e:
        return False