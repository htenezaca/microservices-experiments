import random
from flask import Flask, request
from flask.wrappers import Response
from datetime import datetime
#from flask_restful import Api, Resource
import requests 
import json 
import uuid
import time 
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

users = {
    "valid": {
        "user1": "password1",
        "user2": "password2"
    }, 
    "invalid": {
        "baduser1": "badpassword1",
        "baduser2": "badpassword2"
    }
}

@app.get("/start")
def start():
    app.logger.info("Cliente web started")
    data = {"message": "Login test running"}
    response = Response(json.dumps(data), status=200, content_type="application/json")
    auth_test(5, 0.5)

    @response.call_on_close
    def on_close():
        app.logger.info("Cliente web finished")
    return response

def auth_test(calls=5, interval=0.5):
    results = {}
    for _ in range(calls):
        # Generate a random uuid
        id = uuid.uuid4()
        app.logger.info(f"Call id {id} generated")
        # Call auth
        type = random.choice([True, False])
        results[id] = call_auth(id, type)
        time.sleep(interval)
    app.logger.info("Auth test finished")

def call_auth(id, valid_call):
    start = datetime.now()
    if valid_call:
        user, passw = random.choice(list(users["valid"].items()))
    else:
        user, passw = random.choice(list(users["invalid"].items()))

    data = {"username": user, "password": passw}
    app.logger.info(data)
    res = requests.post("http://api_gateway/comandos/gestion_usuarios/auth", json=data)
    app.logger.info(res)
    end = datetime.now()
    delta = end - start 
    return {
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta.microseconds,
        "status": res.ok
    }

""" api = Api(app) """

""" @app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I'm the client"} """

""" class Login(Resource):

    def post(self):
        app.logger.info("Login user")

        return {"message": "succesfull"}, 200

api.add_resource(Login, '/login') """