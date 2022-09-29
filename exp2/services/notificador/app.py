from flask import Flask, request
import logging
import requests

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I send notifications to users"}

@app.post("/2fa")
def send_token():
    token = request.json.get("token_2fa", None)
    if(send_notification(token)):
        return {"message":"user notified"}, 200
    else:
        return {"message":"error notifying"}, 500


def send_notification(token_2fa):
    res = requests.get(
        f"http://cliente_web:5000/client_2fa", json={"token_2fa": token_2fa})
    if res.status_code == 200:
        return True
    else:
        return False