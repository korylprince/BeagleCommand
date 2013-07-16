import os, time, datetime
import random, string
import select
import array
from BeagleCommand import Debug
from BeagleCommand.util import Worker
from BeagleCommand.util import Message, Packet, PacketException
from BeagleCommand import pyserial

IDSample = string.letters + string.digits

class Serial(Worker):

    def __init__(self, InQueue, MessageBox):
        super(Serial,self).__init__(InQueue,MessageBox)
        self.port = "/dev/ttyUSB0"
        self.replyStore = dict()

    def buildUp(self):
        self.output('Opening Serial Port: ' + self.port)
        self.serial = pyserial.Serial(self.port, 115200)
        self.serial.nonblocking()

    def tearDown(self):
        self.serial.flush()
        self.serial.close()

    def loop(self):
        if select.select([self.serial],[],[],0.1)[0]:
            try:
                p = Packet(packetstr=self.serial.readline())
                if Debug:
                    self.output('Got Packet ID: {0}, Command: {1}, Arguments: {2}'.format(p.ID, p.command, str(p.args)))
                    exec('self.{0}({1},*{2})'.format(p.command, p.ID, p.args))
            except PacketException as e:
                if Debug:
                    self.output('Invalid Checksum on Packet: ' + e.packetstr)

    def IDgen(self):
        return random.choice(IDSample) + random.choice(IDSample)

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

    def get(self, replyQueue):
        """Tell server to send back latest values"""
        ID = self.IDgen()
        self.replyStore[ID] = replyQueue
        self.send(ID, 'get')

    def reply(self, ID, bytestr):
        """Send reply back to web server"""
        vals = array.array()
        vals.fromstring(bytestr)
        self.replyStore[ID].put(vals.tolist())

    def time(self):
        """Get system time and send it to server"""
        datestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.send('00', 'time', [datestr])
        # wait a second so notimes don't build up
        time.sleep(1)

    def notime(self):
        self.time()

    def reboot(self):
        self.send('00', 'reboot')

    def poweroff(self):
        self.send('00', 'poweroff')