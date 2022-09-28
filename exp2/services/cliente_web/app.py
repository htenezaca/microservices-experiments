from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended import JWTManager
import requests
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)
api = Api(app)


@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I'm the client"}


class Exp2(Resource):
    def get(self):
        app.logger.info("Start authentication from client_web")
        user1 = {"username": "user1", "password": "password1"}
        res = requests.post(
            f"http://api_gateway/comandos/gestion_usuarios/auth", json=user1)
        if res.status_code == 200:
            app.logger.info("Correct credentials")
            return {"message": "Conection succesfull"}, 200
        else:
            app.logger.error("Authentication error")
            return {"error": "Bad username or password"}, 401


class Auth2(Resource):
    def post(self):
        token_2fa = request.json.get("token_2fa")
        if token_2fa is None:
            return {"error": "Bad token_2fa"}, 401
        self.send_token_2fa(token_2fa)
        return {"message": "succesfull"}, 200

    def send_token_2fa(self, token_2fa):
        # app.logger.info("token: " + token_2fa)
        # simulate wrong token_2fa
        # token_2fa = '12345'
        res = requests.post(
            f"http://api_gateway/comandos/gestion_usuarios/validate_auth2", json={"token_2fa": token_2fa})
        if res.status_code == 200:
            app.logger.info("Sending token_2fa from client_web")
            return {"message": "succesfull"}, 200
        else:
            app.logger.error(
                "Token_2fa not sent from client_web or something went wrong")
            return {"error": "Bad token_2fa"}, 401


api.add_resource(Exp2, "/exp2")
api.add_resource(Auth2, "/client_2fa")
