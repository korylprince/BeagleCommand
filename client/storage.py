import sqlite3
import os
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
        self.conn.execute('create table if not exists data (timestamp real primary key, voltage real, used real, charged real, kwhs real);')
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.output('Closing '+self.dbpath)
        self.conn.commit()
        self.conn.close()

    def put(self, row):
        """insert data into database"""
        self.cursor.execute('insert into data (timestamp, voltage, used, charged, kwhs) values (?, ?, ?, ?, ?);',
                (row[0],row[1],row[2],row[3],row[4]))

        self.conn.commit()
