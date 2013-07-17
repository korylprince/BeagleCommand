import sqlite3
import os, datetime
from flask import Flask
from flask import render_template, jsonify, request
import BeagleCommand
from BeagleCommand.util import Message

app = Flask(__name__)

dbpath = '{0}/storage/{1}-web.db'.format(os.path.abspath(os.path.dirname(BeagleCommand.__file__)),datetime.datetime.now().strftime('%m.%d.%Y'))
conn = sqlite3.connect(dbpath)

@app.route('/')
def index():
    data = getData()
    return render_template('index.html',data=data,v=data['voltageData'][0][1],uwh=round(data['usedwatthData'][0][1],2),
            cwh=round(data['chargedwatthData'][0][1],2),uw=round(data['usedwattData'][0][1],2),
            cw=round(data['chargedwattData'][0][1],2),kwh=round(data['kilowattData'][0][1],2))

@app.route('/get')
def get():
    data = getData()
    data['v'] = round(data['voltageData'][0][1],2)
    data['uwh'] = round(data['usedwatthData'][0][1],2)
    data['cwh'] = round(data['chargedwatthData'][0][1],2)
    data['uw'] = round(data['usedwattData'][0][1],2)
    data['cw'] = round(data['chargedwattData'][0][1],2)
    data['kwh'] = round(data['kilowattData'][0][1],2)
    return jsonify(data)

@app.route('/command')
def command():
    return render_template('command.html')

@app.route('/command', methods=['POST'])
def commandPost():
    m = Message(to=['serial'], msg=[request.form['command'],[0.0]])
    app.MessageBox.put(m)
    return jsonify(status=request.form['command'])

def getData():
    voltage = list()
    motor = list()
    charge = list()
    usedwatth = list()
    chargedwatth = list()
    usedwatt = list()
    chargedwatt = list()
    kilowatt = list()
    for row in conn.execute('select * from data order by timestamp desc limit 60;'):
        t = int(row[0]*1000)
        voltage.append([t,row[1]])
        motor.append([t,row[2]])
        charge.append([t,row[3]])
        usedwatth.append([t,row[4]])
        chargedwatth.append([t,row[5]])
        usedwatt.append([t,row[4]*row[1]])
        chargedwatt.append([t,row[5]*row[1]])
        kilowatt.append([t,row[6]])
    return dict(voltageData=voltage, motorData=motor, chargeData=charge, usedwatthData=usedwatth,
            chargedwatthData=chargedwatth, usedwattData=usedwatt, chargedwattData=chargedwatt, kilowattData=kilowatt)

