from flask import Flask, request
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended import JWTManager
import requests
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
api = Api(app)


@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I send notifications to users"}


class Notification(Resource):
    def post(self):
        token_2fa = request.json.get("token_2fa", None)
        if token_2fa is None:
            return {"error": "Bad token_2fa"}, 401
        self.send_notification(token_2fa)
        return {"message": "succesfull"}, 200

    def send_notification(self, token_2fa):
        res = requests.post(
            f"http://cliente_web:5000/client_2fa", json={"token_2fa": token_2fa})
        if res.status_code == 200:
            app.logger.info("Notification sent")
        else:
            app.logger.error("Error sending notification")
            return {"error": "Action not allowed"}, 401
        return


api.add_resource(Notification, "/2fa")
