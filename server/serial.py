import os, time
import io, select
from threading import Semaphore
from BeagleCommand.server import TimeUpdated, Debug
from worker import Worker
from BeagleCommand.util import Message, Packet, PacketException
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
            try:
                p = Packet(packetstr=self.serial.readline())
                if Debug:
                    self.output('Got Packet ID: {0}, Command: {1}, Arguments: {2}'.format(p.ID, p.command, str(p.args)))
                    exec('self.{0}(*{1})'.format(p.command,p.args))
            except PacketException as e:
                if Debug:
                    self.output('Invalid Checksum on Packet: ' + e.packetstr)

    def send(self,ID,*args):
        if Debug:
            self.output('Serial Out ID: '+str(ID))

    def time(self,t):
        self.output('Got Time. Setting to ' + t)
        os.system('timedatectl set-time "' + t + '"')
        TimeUpdated.set()
