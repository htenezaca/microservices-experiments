from flask import Flask
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.get("/")
def index():
    app.logger.info("Index page accessed")
    return {"message": "Hello World, I send notifications to users"}
