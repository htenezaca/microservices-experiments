from flask import Flask, Response
from datetime import datetime
import random
import csv  
import os

app = Flask(__name__)
threshold = 0.5
filename = 'stats/responses.csv'

header = ['timestamp', 'id', 'result', 'threshold']
if(not os.path.isfile(filename) or os.path.getsize(filename) == 0):
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)


@app.get('/<int:id>')
def hello_world(id):
    random_number = random.random()
    response = Response("OK", status=200)
    
    if(random_number < threshold):
        response = Response("FAIL", status=500)

    with open(filename, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        
        # getting the timestamp
        dt = datetime.now()

        writer.writerow([dt, id, response.status_code, threshold])

    return response 