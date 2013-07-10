import time
import serial, io, select
from threading import Semaphore
from BeagleCommand.server import TimeUpdated, Debug
from worker import Worker
from BeagleCommand.util import Message

class Serial(Worker):

    def __init__(self,InQueue,MessageBox):
        super(Serial,self).__init__(InQueue,MessageBox)
        self.port = "/dev/ttyO2"

    def buildUp(self):
        self.output('Opening Serial Port: ' + self.port)
        self.serial = serial.Serial('/dev/ttyS1', 19200)
        self.serial.nonblocking()
        self.serialIO = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
        self.ouput('Waiting for time...')

    def loop(self):
        if select.select([self.serial],[],[],timeout=0.1)[0]:
            self.output(serl.serialIO.readline())

    def send(self,ID,*args):
        if Debug:
            self.output('Serial Out ID: '+str(ID))

