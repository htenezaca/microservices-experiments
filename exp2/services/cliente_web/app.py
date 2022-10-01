from flask import Flask, json, request, Response
import requests
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

BASE_URL = "http://api_gateway"
GU_URL = BASE_URL + "/comandos/gestion_usuarios"

@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I'm the client"}

@app.post("/client_2fa")
def received_token():
    payload = request.json
    token2fa = payload["token_2fa"]
    app.logger.info(f"received token2fa: {payload}")
    res = Response(json.dumps({"message": "token received"}), status=200)

    @res.call_on_close
    def on_close():
        # Confirm the login now that we have a token
        validate_res = requests.post(GU_URL + '/auth/validate', json={"username": "ronald", "token_2fa": token2fa})
        authdata = validate_res.json()
        auth_token = authdata["jwt"]
        if validate_res.status_code == 200:
            app.logger.info("Login confirmed, received authentication token " + auth_token)
            # Attempt accessing my personal information
            res = requests.get(GU_URL + '/me', headers={"Authorization": f"Bearer {auth_token}"})
            if res.status_code == 200:
                app.logger.info("Personal information accessed: " + json.dumps(res.json()))
            else:
                app.logger.error("Personal information access failed")
        else:
            app.logger.error("Login failed with token_2fa " + token2fa)

    return res
