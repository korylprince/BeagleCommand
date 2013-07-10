import time
import io, select
from threading import Semaphore
from BeagleCommand.server import TimeUpdated, Debug
from worker import Worker
from BeagleCommand.util import Message
from BeagleCommand import pyserial

class Serial(Worker):

    def __init__(self,InQueue,MessageBox):
        super(Serial,self).__init__(InQueue,MessageBox)
        self.port = "/dev/ttyO2"

    def buildUp(self):
        self.output('Opening Serial Port: ' + self.port)
        self.serial = pyserial.Serial('/dev/ttyO2', 19200)
        self.serial.nonblocking()
        self.output('Waiting for time...')

    def loop(self):
        if select.select([self.serial],[],[],0.1)[0]:
            recv = self.serial.readline()

    def send(self,ID,*args):
        if Debug:
            self.output('Serial Out ID: '+str(ID))
