# Web-related code.

# sudo apt-get install python3-flask
from flask import Flask, request
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return """
  <form action='/hello' method='post'>
    Enter your name: <input type="text" name="name" id="name" required>
    </br>
    <input type="submit" value="say hello">
  </form>
"""

@flask_app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')
    return "Hello, %s!" % (name)

def init():
    global flask_app
    pass
    # flask_app.run(host="0.0.0.0")

