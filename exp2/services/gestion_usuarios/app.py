from email import header
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, jwt_required
from flask_jwt_extended import JWTManager
import requests
import logging
import random
import csv
import os
import string


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.config["JWT_SECRET_KEY"] = "secret-jwt"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)
api = Api(app)

filename = "./tokens_data.csv"
header = ["user", "result"]
users = {
}

@app.before_first_request
def init():
    # remove the file and create a new one
    os.remove(filename)
    with open(filename, 'w', encoding="UTF8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I authenticate the users"}, 200

class Auth(Resource):

    def post(self):
        app.logger.info("Authenticating user")
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if username != password:
            return {"error": "Bad username or password"}, 401
            
        token = self.generate_token()
        users[username] = token

        return self.send_token_2fa(username, token)

    def send_token_2fa(self, user, token_2fa):
        
        app.logger.info("Sending token_2fa to notificador")
        res = requests.post(
            f"http://notificador:5000/2fa", json={"user": user,"token_2fa": token_2fa})
        if res.status_code == 200:
            app.logger.info("Token_2fa sent")
            return {"message": "succesfull"}, 200
        else:
            app.logger.error("Token_2fa error")
            return {"error": "Token_2fa not sent"}, 401

    def get_token_2fa(self, user):
        if user in users:
            return users[user]
        return None
    
    def generate_token(self):
        letters = string.ascii_lowercase
        token = ''.join(random.choice(letters) for i in range(6))
        return token

class ValidateAuth2(Resource):

    auth = Auth()

    def post(self):
        username = request.json.get('username')
        token_2fa = request.json.get('token_2fa')
        expected_token = self.auth.get_token_2fa(username)
        if expected_token == None or token_2fa != expected_token:
            write_csv({"user":username,"result":False})
            app.logger.error("Token_2fa does not match")
            return {"error": "Two_token doesn't match"}, 401
        write_csv({"user":username,"result":True})
        app.logger.info("Token_2fa validated")
        return {"message": "authenticated"}, 200

api.add_resource(Auth, '/auth')
api.add_resource(ValidateAuth2, '/validate_auth2')


def write_csv(data):
    with open(filename, "a") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writerow(data)