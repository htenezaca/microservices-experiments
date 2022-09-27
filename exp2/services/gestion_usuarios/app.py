from flask import Flask, request
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


class Auth(Resource):
    def post(self):
        app.logger.info("Authenticating user")
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if username not in users or password != users[username]["password"]:
            return {"error": "Bad username or password"}, 401
        access_token = create_access_token(identity=username)
        response = self.notificar(access_token)
        # No send access_token, just for example
        return {"message": "succesfull"}, 200
        # return {"access_token": access_token}, 200

    def notificar(self, token):
        # TODO: Send the request for double authentication Chamge this!
        # Get the response from the notificador service
        # return requests.post("http://notificador:5000/comandos/notificador", headers={"Authorization": f"Bearer {token}"})
        return requests.get(f"http://api_gateway/comandos/notificador", headers={"Authorization": f"Bearer {token}"})


class TwoFactor(Resource):

    two_factor = '123456'

    @jwt_required()
    def get(self):
        return {"token": self.two_factor}, 200

    def get_value(self):
        return self.two_factor


class Auth2(Resource):

    two_factor_generated = TwoFactor()

    @jwt_required()
    def get(self):
        two_factor_input = request.args.get('token')
        if two_factor_input != self.two_factor_generated.get_value():
            return {"error": "Two_token doesn't match"}, 401
        self.notifyToClient(self.get_token_header())
        return {"message": self.get_token_header()}, 200

    def get_token_header(self):
        return request.headers.get('Authorization')

    def notifyToClient(self, token):
        # TODO: Send the request for double authentication Chamge this!
        return requests.get(f"http://api_gateway/comandos/client_web", headers={"Authorization": f"{token}"})


class NotifyToClient(Resource):

    @jwt_required()
    def post(self):
        app.logger.info("Sending message to user")
        token = request.headers.get("Authorization", None)
        if token is None:
            return {"error": "Missing token"}, 401
        if self.notify(token).ok:
            return {"message": "Message sent"}, 200
        return {"error": "Error sending message"}, 500

    def notify(self, token):
        # TODO: Send the notification to the user Change this!
        # return requests.post("http://notificador:5000/comandos/cliente_web")
        return requests.get(f"http://api_gateway/comandos/cliente_web")


api.add_resource(Auth, '/auth')
api.add_resource(NotifyToClient, '/notificar')
api.add_resource(Auth2, '/auth2')
api.add_resource(TwoFactor, '/two_factor')
