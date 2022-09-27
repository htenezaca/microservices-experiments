from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token
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
    return {"message": "Hello World, I authenticate the users"}


class AuthResource(Resource):
    def post(self):
        app.logger.info("Authenticating user")
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if username not in users or password != users[username]["password"]:
            return {"error": "Bad username or password"}, 401
        access_token = create_access_token(identity=username)
        return {"access_token": access_token}, 200


api.add_resource(AuthResource, '/auth')
