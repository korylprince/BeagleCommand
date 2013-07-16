import sqlite3
import os
import time
from datetime import datetime
import array
import BeagleCommand
from BeagleCommand import TimeUpdated, QuitinTime
from BeagleCommand.util import Worker, Message

# hours per second
hps = 1.0/(60*60)

class Storage(Worker):
    """class that handles saving data and data statistics"""

    def __init__(self, InQueue, MessageBox):
        super(Storage,self).__init__(InQueue,MessageBox)
        self.messageBound = True

        # initialize variables
        self.data = []
        self.time = time.time()
        self.voltage = 0.0
        self.usedAmps = 0.0
        self.chargedAmps = 0.0
        self.kwhs = 0.0

        # set commit timer
        self.lastcommit = time.time()

    def buildUp(self):
        self.output('Waiting for time to update...')
        # wait for time to come
        while not TimeUpdated.is_set() and not QuitinTime.is_set():
            TimeUpdated.wait(0.5)
        else:
            # if time never came and it's time to quit, skip tear down
            if QuitinTime.is_set():
                self.tearDown = lambda : None
                return
        self.output('Time updated... Starting')
        self.dbpath = '{0}/storage/{1}.db'.format(os.path.abspath(os.path.dirname(BeagleCommand.__file__)),datetime.now().strftime('%m.%d.%Y'))
        self.output('Using '+self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)
        self.conn.execute('create table if not exists data (timestamp real primary key, duration real, voltage real, used real, charged real);')
        self.cursor = self.conn.cursor()
        for row in self.cursor.execute('select timestamp, duration, voltage, used, charged from data order by timestamp;'):
            self.process(row)

    def tearDown(self):
        self.output('Closing '+self.dbpath)
        self.conn.commit()
        self.conn.close()

    def get(self, ID):
        """send serial the latest numbers"""
        m = Message(to=['serial'],msg=['send', ID, 'reply', [array.array('f',
            [self.time, self.voltage, self.usedAmps, self.chargedAmps, self.kwhs]).tostring()]])
        self.MessageBox.put(m)

    def put(self, row):
        """insert data into database"""
        self.cursor.execute('insert into data (timestamp, duration, voltage, used, charged) values (?, ?, ?, ?, ?);',
                (row[0],row[1],row[2],row[3],row[4]))
        self.process(row)

        # commit to db every 10 seconds
        if time.time() - self.lastcommit > 10:
            self.conn.commit()
            self.lastcommit = time.time()

    def process(self, row):
        """add data to current totals"""
        self.data.append([row[0],row[1],row[2],row[3],row[4]])
        self.time, self.voltage, self.usedAmps, self.chargedAmps = row[0], row[2], row[3], row[4]
        # v * (charged-used amps) * duration * hps / 1000 = kWh
        self.kwhs += row[2]*(row[4]-row[3])*row[1]*hps/1000
