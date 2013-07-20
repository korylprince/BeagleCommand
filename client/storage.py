import sqlite3
import os, time
from datetime import datetime
import BeagleCommand
from BeagleCommand.util import Worker

class Storage(Worker):
    """class that handles saving data and data statistics"""

    def __init__(self, InQueue, MessageBox):
        super(Storage,self).__init__(InQueue,MessageBox)
        self.messageBound = True

    def buildUp(self):
        self.dbpath = '{0}/storage/{1}-web.db'.format(os.path.abspath(os.path.dirname(BeagleCommand.__file__)),datetime.now().strftime('%m.%d.%Y'))
        self.output('Using '+self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)
        self.conn.execute('create table if not exists data (time real primary key, voltage real, used real, charged real, usedwhs real, chargedwhs real, totalwhs real);')
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.output('Closing '+self.dbpath)
        self.conn.commit()
        self.conn.close()

    def put(self, row):
        """insert data into database"""
        self.cursor.execute('insert into data (time, voltage, used, charged, usedwhs, chargedwhs, totalwhs) values (?, ?, ?, ?, ?, ?, ?);',
                (row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        self.conn.commit()

    def reset(self):
        self.output('Reseting... Closing '+self.dbpath)
        self.conn.commit()
        self.conn.close()
        
        os.rename(self.dbpath,self.dbpath+str(time.time()))

        self.output('Using '+self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)
        self.conn.execute('create table if not exists data (time real primary key, duration real, voltage real, used real, charged real);')
        self.cursor = self.conn.cursor()

