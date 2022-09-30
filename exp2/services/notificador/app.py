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
    user = request.json.get("user", None)
    token = request.json.get("token_2fa", None)
    if(send_notification(user, token)):
        return {"message":"user notified"}, 200
    else:
        return {"message":"error notifying"}, 500


def send_notification(user, token_2fa):
    app.logger.info("posting token " + token_2fa + " to user " + user)
    res = requests.post(
        f"http://cliente_web:5000/client_2fa", json={"user": user, "token_2fa": token_2fa})
    if res.status_code == 200:
        return True
    else:
        return True