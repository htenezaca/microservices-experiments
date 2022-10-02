import os
import random
import string
from urllib.parse import parse_qs, urlparse
from flask import Flask, json, request, Response
from datetime import datetime
import json 
import uuid
import time 
import requests
import logging
import csv

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
BASE_URL = "http://api_gateway"
GU_URL = BASE_URL + "/comandos/gestion_usuarios"

# En el contexto del experimento, los usuarios validos tienen usuario y password iguales
users = {
    "valid": {
        "user1": "user1",
        "usuario": "usuario",
        "admin": "admin",
        "tester": "tester",
        "oper": "oper"
    }, 
    "invalid": {
        "baduser1": "badpassword1",
        "badusuario": "badpassword",
        "badadmin": "pass",
        "badtester": "admin",
        "badoper": "Oper"
    }
}

filename = "./results.csv"
header_file = ["id", "start", "end", "delta", "status", "request", "response", 
               "type", "expected", "received", "assert"]

@app.before_first_request
def init():    
    try:
        os.remove(filename)
    except:
        pass

    with open(filename, 'w', encoding="UTF8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header_file)
        writer.writeheader()

@app.get("/start")
def start():
    app.logger.info("Cliente web started")
    
    calls = request.args.get('calls', type=int)
    data = {"message": f"Login test running {calls} calls"}
    response = Response(json.dumps(data), status=200, content_type="application/json")
    auth_test(calls, 0.2)

    @response.call_on_close
    def on_close():
        app.logger.info("Cliente web finished")
    return response

def auth_test(calls=5, interval=0.5):
    #results = {}
    for _ in range(calls):
        # Generate a random uuid
        id = str(uuid.uuid4())
        app.logger.info(f"Call id {id} generated")
        # Call auth
        type = random.choice([True, False])
        #results[id] = call_auth(id, type)
        write_csv(call_auth(id, type))
        time.sleep(interval)
    app.logger.info("Auth test finished")
    #app.logger.info(results)

def call_auth(id, valid_call):
    start = datetime.now()
    if valid_call:
        user, passw = random.choice(list(users["valid"].items()))
    else:
        user, passw = random.choice(list(users["invalid"].items()))

    data = {"username": user, "password": passw}
    app.logger.info(data)
    res = requests.post(GU_URL + "/auth", json=data)
    app.logger.info(res)
    end = datetime.now()
    delta = end - start 
    expected = 200 if valid_call else 401
    return {
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta.microseconds,
        "status": res.ok,
        "request": data,
        "response": res.json(),
        "type": "Usuario valido" if valid_call else "Usuario invalido",
        "expected": expected,
        "received": res.status_code,
        "assert": True if expected == res.status_code else False
    }

@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I'm the client"}

@app.post("/client_2fa")
def received_token():
    id = str(uuid.uuid4())
    payload = request.json
    user = payload["user"]
    token2fa = payload["token_2fa"]
    app.logger.info(f"received token2fa: {payload}")
    res = Response(json.dumps({"message": "token received"}), status=200)

    @res.call_on_close
    def on_close():
        response = call_auth_2fa(id, user, token2fa)
        write_csv(response)
        if response["status"]:
            response_resource = call_resource(id, response["response"]["jwt"])
            write_csv(response_resource)        

    return res

def call_auth_2fa(id, user, token2fa):
    app.logger.info("call auth 2fa starting")
    start = datetime.now()
    options = [
        "Autenticacion valida",
        "Deteccion de doble factor nulo", 
        "Deteccion de doble factor invalido",
        "Deteccion de match incorrecto de doble factor por usuario valido diferente",
        "Deteccion de match incorrecto de doble factor por usuario invalido"
    ]
    type = random.choice(options)
    expected = 401

    if type == "Autenticacion valida":
        expected = 200
    elif type == "Deteccion de doble factor nulo":
        token2fa = None 
    elif type == "Deteccion de doble factor invalido":
        letters = string.ascii_lowercase
        token2fa = ''.join(random.choice(letters) for i in range(6))
    elif type == "Deteccion de match incorrecto de doble factor por usuario valido diferente":
        user_new = user
        while user == user_new:
            user = random.choice(list(users["valid"].items()))[0]
    elif type == "Deteccion de match incorrecto de doble factor por usuario invalido":
        user = random.choice(list(users["invalid"].items()))[0]

    data = {"username": user, "token_2fa": token2fa}
    app.logger.info(type)
    app.logger.info(data)
    res = requests.post(GU_URL + '/auth/validate', json=data)
    app.logger.info(res)
    end = datetime.now()
    delta = end - start 

    return {
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta.microseconds,
        "status": res.ok,
        "request": data,
        "response": res.json(),
        "type": type,
        "expected": expected,
        "received": res.status_code,
        "assert": True if expected == res.status_code else False
    }

def call_resource(id, auth_token):    
    start = datetime.now()
    app.logger.info("Login confirmed, received authentication token " + auth_token)
    # Attempt accessing my personal information
    res = requests.get(GU_URL + '/me', headers={"Authorization": f"Bearer {auth_token}"})
    if res.status_code == 200:
        app.logger.info("Personal information accessed: " + json.dumps(res.json()))
    else:
        app.logger.error("Personal information access failed")
    
    end = datetime.now()
    delta = end - start 
    expected = 200

    return {
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta.microseconds,
        "status": res.ok,
        "request": auth_token,
        "response": res.json(),
        "type": "Acceso satisfactorio",
        "expected": expected,
        "received": res.status_code,
        "assert": True if expected == res.status_code else False
    }

def write_csv(data):
    with open(filename, "a") as f:
        writer = csv.DictWriter(f, fieldnames=header_file)
        writer.writerow(data)
