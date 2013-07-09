import sqlite3
import os
from datetime import datetime
import BeagleCommand
from BeagleCommand.server import TimeUpdated
from worker import Worker

class Storage(Worker):
    """class that handles saving data and data statistics"""

    def __init__(self,InQueue,MessageBox):
        super(Storage,self).__init__(InQueue,MessageBox)
        self.messageBound = True

    def buildUp(self):
        self.output('Waiting for time to update...')
        TimeUpdated.wait()
        self.output('Time updated... Starting')
        self.dbpath = '{0}/storage/{1}.db'.format(os.path.abspath(os.path.dirname(BeagleCommand.__file__)),datetime.now().strftime('%m.%d.%Y'))
        self.output('Using '+self.dbpath)
