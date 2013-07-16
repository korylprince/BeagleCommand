from flask import Flask
from flask import render_template, jsonify, request
from BeagleCommand.util import Message

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get')
def get():
    return jsonify()

@app.route('/command')
def command():
    return render_template('command.html')

@app.route('/command', methods=['POST'])
def commandPost():
    m = Message(to=['serial'], msg=[request.form['command'],[0.0]])
    app.MessageBox.put(m)
    return jsonify(status=request.form['command'])
