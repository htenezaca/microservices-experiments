from flask import Flask
from flask.wrappers import Response
from datetime import datetime
import random
import csv
import os
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
threshold = 0.25
filename = "./responses.csv"

@app.before_first_request
def init():
    # remove the file and create a new one
    os.remove(filename)
    with open(filename, 'w', encoding="UTF8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()


header = ["id", "start", "end", "delta", "status"]
@app.get("/alert/<id>")
def process(id):
    # Global storage persist over threads
    start = datetime.now()
    random_number = random.random()
    response = Response("OK", status=200)
    status = True

    if random_number < threshold:
        response = Response("FAIL", status=500)
        status = False

    end = datetime.now()

    req_result = {
            "id": id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "delta": (end - start).microseconds,
            "status": status,
        }

    save_result(req_result)
    return response

def save_result(result):
    with open(filename, 'a', encoding="UTF8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writerow(result)
