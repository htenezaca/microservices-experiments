from flask import Flask, redirect
import random

app = Flask(__name__)
threshold = 0.5

@app.get('/')
def hello_world():
    random_number = random.random()
    print(random_number)
    if(random_number < threshold):
        if(random_number < threshold/2):
            #ECONNREFUSED
            return redirect('http://127.0.0.1:8000')
        else:
            #Timeout
            return redirect('http://10.0.0.0')
    else:
        #Ok
        return {'message': 'Hello, World! from gestion_accionables'}
