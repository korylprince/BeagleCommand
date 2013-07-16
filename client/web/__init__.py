from flask import Flask
from flask import render_template, jsonify, request
import Queue
from BeagleCommand.util import Message
from BeagleCommand.client import SerialIn

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command')
def command():
    return render_template('command.html')

@app.route('/command', methods=['POST'])
def commandPost():
    m = Message(['serial'],[request.form['command']])
    SerialIn.put(m)
    return jsonify(status=request.form['command'])
