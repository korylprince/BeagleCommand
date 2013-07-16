import os, time
import select
from BeagleCommand import TimeUpdated, Reboot, PowerOff, Debug
from BeagleCommand.util import Worker, Message, Packet, PacketException
from BeagleCommand import pyserial

class Serial(Worker):

    def __init__(self, InQueue, MessageBox):
        super(Serial,self).__init__(InQueue,MessageBox)
        self.port = "/dev/ttyO2"

    def buildUp(self):
        self.output('Opening Serial Port: ' + self.port)
        self.serial = pyserial.Serial(self.port, 115200)
        self.serial.nonblocking()
        self.output('Waiting for time...')

    def tearDown(self):
        self.serial.flush()
        self.serial.close()

    def loop(self):
        if select.select([self.serial],[],[],0.1)[0]:
            try:
                p = Packet(packetstr=self.serial.readline())
                if Debug:
                    self.output('Got Packet ID: {0}, Command: {1}, Arguments: {2}'.format(p.ID, p.command, str(p.args)))
                    exec('self.{0}("{1}",*{2})'.format(p.command, p.ID, p.args))
            except PacketException as e:
                if Debug:
                    self.output('Invalid Checksum on Packet: ' + e.packetstr)

    def send(self, ID, command, *args):
        """Send serial packet. If time to set, send request."""
        try:
            p = Packet(ID, command, *args)
            if Debug:
                self.output('Serial Out Packet: '+str(p))
            self.serial.write(str(p))
            self.serial.flush()
        except PacketException as e:
            if Debug:
                self.output('Invalid Checksum on Created Packet: ' + e.packetstr)

    def get(self, ID):
        """Tell storage to send back latest values"""
        if not TimeUpdated.is_set():
            self.send(ID, 'notime')
            return
        m = Message(to=['storage'],msg=['get', ID])
        self.MessageBox.put(m)

    def time(self, ID, timestr):
        """Set system time"""
        self.output('Got Time. Setting to ' + timestr)
        if os.system('timedatectl set-time "' + timestr + '"') == 0:
            TimeUpdated.set()
        else:
            self.output('Time update failed')

    def reboot(self, ID):
        QuitinTime.set()
        Reboot.set()

    def poweroff(self, ID):
        QuitinTime.set()
        PowerOff.set()

