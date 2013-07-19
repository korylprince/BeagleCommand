import sqlite3
import os, datetime
from flask import Flask
from flask import render_template, jsonify, request
from jinja2.environment import Environment
import BeagleCommand
from BeagleCommand.util import Message

app = Flask(__name__)
environment = Environment()

dbpath = '{0}/storage/{1}-web.db'.format(os.path.abspath(os.path.dirname(BeagleCommand.__file__)),datetime.datetime.now().strftime('%m.%d.%Y'))
conn = sqlite3.connect(dbpath)

def nl(x):
    return x.replace('\\n','\n')

app.jinja_env.filters['nl'] = nl

@app.route('/')
def index():
    chartjs, updatejs = getJS() 
    return render_template('index.html',data=getData(), chartjs=chartjs, updatejs=updatejs)

@app.route('/get')
def get():
    return jsonify(getData())

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
    used = list()
    charged = list()
    usedwh = list()
    chargedwh = list()
    usedw = list()
    chargedw = list()
    totalwh = list()
    for row in conn.execute('select * from data order by time desc limit 60;'):
        t = int(row[0]*1000)
        voltage.append([t,row[1]])
        used.append([t,row[2]])
        charged.append([t,row[3]])
        usedwh.append([t,row[4]])
        chargedwh.append([t,row[5]])
        usedw.append([t,row[4]*row[1]])
        chargedw.append([t,row[5]*row[1]])
        totalwh.append([t,row[6]])

    data = dict(voltageData=voltage, usedData=used, chargedData=charged, usedwhData=usedwh,
            chargedwhData=chargedwh, usedwData=usedw, chargedwData=chargedw, totalwhData=totalwh)

    data['t'] = datetime.datetime.fromtimestamp(data['voltageData'][0][0]/1000.0).strftime('%M:%S')
    data['v'] = round(data['voltageData'][0][1],2)
    data['uwh'] = round(data['usedwhData'][0][1],2)
    data['cwh'] = round(data['chargedwhData'][0][1],2)
    data['uw'] = round(data['usedwData'][0][1],2)
    data['cw'] = round(data['chargedwData'][0][1],2)
    data['twh'] = round(data['totalwhData'][0][1],2)
    return data

def getJS():
    chartjs = []
    chartjs.append(chartTemplate.format(name="voltage", title="Voltage", y="Volts (V)"))
    chartjs.append(chartTemplate.format(name="used", title="Used Amps", y="Amps (A)"))
    chartjs.append(chartTemplate.format(name="charged", title="Charged Amps", y="Amps (A)"))
    chartjs.append(chartTemplate.format(name="usedwh", title="Used Watt Hours", y="Watt Hours (Wh)"))
    chartjs.append(chartTemplate.format(name="chargedwh", title="Charged Watt Hours", y="Watt Hours (Wh)"))
    chartjs.append(chartTemplate.format(name="usedw", title="Used Watts", y="Watts (W)"))
    chartjs.append(chartTemplate.format(name="chargedw", title="Charged Watts", y="Watts (W)"))
    chartjs.append(chartTemplate.format(name="totalwh", title="Total (Net) Watt Hours", y="Watt Hours (Wh)"))

    updatejs = []
    updatejs.append(updateTemplate.format(name="voltage"))
    updatejs.append(updateTemplate.format(name="used"))
    updatejs.append(updateTemplate.format(name="charged"))
    updatejs.append(updateTemplate.format(name="usedwh"))
    updatejs.append(updateTemplate.format(name="chargedwh"))
    updatejs.append(updateTemplate.format(name="usedw"))
    updatejs.append(updateTemplate.format(name="chargedw"))
    updatejs.append(updateTemplate.format(name="totalwh"))

    return ''.join(chartjs), ''.join(updatejs)

chartTemplate = """
    var {name}Chart = $.jqplot('{name}-chart', [data.{name}Data], {{
        title: '{title}',
        axesDefaults: {{
            labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
            tickRenderer: $.jqplot.CanvasAxisTickRenderer,
            tickOptions: {{
                angle: -30
            }}
        }},
        highlighter: {{
            show: true
        }},
        axes:{{
            xaxis:{{
                label:'Time',
                renderer: $.jqplot.DateAxisRenderer,
                tickOptions: {{
                    formatString: '%M:%S'
                }}
            }},
            yaxis:{{
                label:'{y}'
            }}
        }}}});

"""
updateTemplate = """
        {name}Chart.series[0].data = data.{name}Data;
        {name}Chart.resetAxesScale();
        {name}Chart.replot();
"""

