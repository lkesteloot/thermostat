# Web-related code.

import threading
import json

import db

# sudo apt-get install python3-flask
from flask import Flask, request, g
app = Flask(__name__)

def get_db():
    conn = getattr(g, "_database", None)
    if conn is None:
        conn = db.connect()
        g._database = conn
    return conn

@app.route('/')
def index():
    return """
  <form action='/hello' method='post'>
    Enter your name: <input type="text" name="name" id="name" required>
    </br>
    <input type="submit" value="say hello">
  </form>
"""

@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')
    return "Hello, %s!" % (name)

@app.route('/api/temp')
def api_temp():
    print("Handler thread", threading.current_thread().ident)
    samples = db.get_recent_data(get_db(), 60*24)
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
    print("Init thread", threading.current_thread().ident)
    app.run(host="0.0.0.0", debug=True, use_reloader=False)

def init():
    print("Main thread", threading.current_thread().ident)
    threading.Thread(target=start).start()

