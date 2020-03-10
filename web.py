# Web-related code.

import threading
import json

import db

# sudo apt-get install python3-flask
from flask import Flask, request, g, current_app
app = Flask(__name__)

def get_db():
    conn = getattr(g, "_database", None)
    if conn is None:
        conn = db.connect()
        g._database = conn
    return conn

@app.route("/")
def index():
    return current_app.send_static_file("index.html")

@app.route("/api/temp")
def api_temp():
    count = request.args.get("count", default=60*24, type=int)
    samples = db.get_recent_data(get_db(), count)
    data = {
            "samples": [sample.to_object() for sample in samples],
    }
    return json.dumps(data)

@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, "_database", None)
    if conn is not None:
        conn.close()

def start():
    global app
    app.run(host="0.0.0.0", debug=True, use_reloader=False)

def init():
    threading.Thread(target=start).start()

