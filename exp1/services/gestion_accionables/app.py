from flask import Flask, Response
import random

app = Flask(__name__)
threshold = 0.5

@app.get('/<int:id>')
def hello_world(id):
    random_number = random.random()
    print(id)
    if(random_number < threshold):
        # La clave es devolver un 500 para que nginx lo atrape
        return Response("FAIL", status=500)
    else:
        return Response("OK", status=200)
