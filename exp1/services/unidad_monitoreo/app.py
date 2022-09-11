from flask import Flask
from flask.wrappers import Response
from datetime import datetime
import requests
import os
import uuid
import time
import csv
import json
import logging

app = Flask(__name__)
filename = "./input.csv"
app.logger.setLevel(logging.INFO)
header = ["id", "start", "end", "delta", "status"]

@app.get("/start")
def start():
    alerts = int(os.environ.get("ALERTS_TO_SEND", 100))
    interval = os.environ.get("ALERTS_INTERVAL_SECONDS", 0.3)
    data = {"message": "Starting stress test", "interval": interval, "alerts": alerts}
    response = Response(json.dumps(data), status=200, content_type="application/json")

    @response.call_on_close
    def on_close():
        stress_test(alerts, interval)

    return response


# Generate a random alert and record it's time taken
def generate_alert(id):
    start = datetime.now()
    res = requests.get(f"http://api_gateway/comandos/gestion_accionables/alert/{id}")
    end = datetime.now()
    delta = end - start
    return {
        "id": id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "delta": delta.microseconds,
        "status": res.ok,
    }

def stress_test(alerts=100, interval=0.5):
    results = {}
    # Check the environment variable ALERT_PER_SECOND
    for _ in range(alerts):
        # Generate a random uuid
        id = uuid.uuid4()
        app.logger.info(f"Alert {id} generated")
        # Generate an alert
        results[id] = generate_alert(id)
        # Sleep for the time it takes to generate the next alert
        time.sleep(interval)

    app.logger.info("Stress test finished")
    write_csv(results)

def write_csv(results):
    with open(filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for result in results.values():
            writer.writerow(result)
