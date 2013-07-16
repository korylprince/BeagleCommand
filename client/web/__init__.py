from flask import Flask
from flask import render_template, jsonify, request
import Queue
from BeagleCommand.client import d

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get')
def get():
    q = Queue.Queue()
    d.serial.get(q)
    d.serial.loop()
    vals = q.get_nowait()
    return jsonify(time=int(round(vals[0]*1000)),
            voltage=vals[1], motorAmps=vals[2], chargeAmps=vals[3], kwhs=vals[4])

@app.route('/command')
def command():
    return render_template('command.html')

@app.route('/command', methods=['POST'])
def commandPost():
    exec('d.serial.{0}()'.format(request.form['command']))
    return jsonify(status=request.form['command'])
