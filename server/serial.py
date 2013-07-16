import os, time
import select
from BeagleCommand import TimeUpdated, QuitinTime, Reboot, PowerOff, Debug
from BeagleCommand.util import Worker, Message, Packet, PacketException
from BeagleCommand import pyserial

class Serial(Worker):

    def __init__(self, InQueue, MessageBox):
        super(Serial,self).__init__(InQueue,MessageBox)
        self.port = "/dev/ttyO2"

    def buildUp(self):
        self.output('Opening Serial Port: ' + self.port)
        self.serial = pyserial.Serial(self.port, 115200)
        self.serial.timeout = 0.01
        self.output('Waiting for time...')

    def tearDown(self):
        self.serial.flush()
        self.serial.close()

    def loop(self):
        if select.select([self.serial],[],[],0.1)[0]:
            try:
                packetstr = self.readline()
                p = Packet(packetstr=packetstr)
                if Debug:
                    self.output('Got Packet: Command: {0}, Value: {1}'.format(p.command, str(p.val)))
                if '-' in p.command:
                    command, typestr = p.command.split('-')
                    exec('self.{0}(\'{1}\',\'{2}\')'.format(command, typestr, p.val))
                else:
                    exec('self.{0}(\'{1}\')'.format(p.command, p.val))
            except PacketException as e:
                if Debug:
                    self.output('{0}: {1}'.format(e.__class__.__name__, repr(e.errstr)))

    def readline(self):
        """Read in 6-byte packet"""
        packetstr = []
        while len(packetstr) != 6:
            s = self.serial.read(1)
            packetstr.append(s)
            if s == '':
                if Debug:
                    self.output('Received Packet of invalid length: ' + repr(''.join(packetstr)))
                return
        return ''.join(packetstr)

    def send(self, command, val):
        """Send serial packet. If time not set, send request."""
        p = Packet(command, val)
        if Debug:
            self.output('Serial Out Packet: ' + repr(str(p)))
        self.serial.write(str(p))
        self.serial.flush()

    def get(self, typestr, val):
        """Tell storage to send back latest values"""
        if not TimeUpdated.is_set():
            self.send('notime', 0.0)
            return
        m = Message(to=['storage'],msg=['get', typestr])
        self.MessageBox.put(m)

    def time(self, val):
        """Set system time"""
        d = datetime.datetime.fromtimestamp(val)
        timestr = d.strftime('%Y-%m-%d %H:%M:%S')
        self.output('Got Time. Setting to ' + timestr)
        if os.system('timedatectl set-time "' + timestr + '"') == 0:
            TimeUpdated.set()
        else:
            self.output('Time update failed')

    def reboot(self, val):
        QuitinTime.set()
        Reboot.set()

    def poweroff(self, val):
        QuitinTime.set()
        PowerOff.set()
