from email import header
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

users = {
    "user1": {"password": "password1"},
    "user2": {"password": "password2"},
}


@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I authenticate the users"}, 200


class TwoFactor():

    two_factor = '123456'

    def get_value(self):
        return self.two_factor


class Auth(Resource):
    token_2fa = TwoFactor()

    def post(self):
        app.logger.info("Authenticating user")
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if username not in users or password != users[username]["password"]:
            return {"error": "Bad username or password"}, 401
        access_token = create_access_token(identity=username)
        response = self.send_token_2fa(
            access_token, self.token_2fa.get_value())
        # No send access_token, just for example
        # return {"access_token": access_token}, 200
        return {"message": "succesfull"}, 200

    def send_token_2fa(self, token, token_2fa):
        # TODO: Send the request for double authentication Chamge this!
        app.logger.info("Sending token_2fa to notificador")
        res = requests.post(
            f"http://notificador:5000/2fa", json={"token_2fa": token_2fa})
        if res.status_code == 200:
            app.logger.info("Token_2fa sent")
            return {"message": "succesfull"}, 200
        else:
            app.logger.error("Token_2fa error")
            return {"error": "Token_2fa not sent"}, 401

    def get_token_2fa(self):
        return self.token_2fa.get_value()


class ValidateAuth2(Resource):

    auth = Auth()

    def post(self):
        token_2fa = request.json.get('token_2fa')
        if token_2fa != self.auth.get_token_2fa():
            app.logger.error("Token_2fa does not match")
            return {"error": "Two_token doesn't match"}, 401
        app.logger.info("Token_2fa validated")
        return {"message": self.get_token_header()}, 200

    def get_token_header(self):
        return request.headers.get('Authorization')


api.add_resource(Auth, '/auth')
api.add_resource(ValidateAuth2, '/validate_auth2')
