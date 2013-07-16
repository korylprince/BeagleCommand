import os, time
import datetime
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
        self.serial = pyserial.Serial(self.port, 19200)
        self.serial.timeout = 0.5
        self.output('Waiting for time...')

    def tearDown(self):
        self.serial.flush()
        self.output('Closing Serial Port: ' + self.port)
        self.serial.close()

    def loop(self):
        self.readSerial()

    def get(self, typestr, val):
        """Tell storage to send back latest values"""
        if not TimeUpdated.is_set():
            self.send('notime', 0.0)
            return
        m = Message(to=['storage'],msg=['get', typestr])
        self.MessageBox.put(m)

    def time(self, val):
        """Set system time"""
        self.output(repr(type(val)))
        d = datetime.datetime.fromtimestamp(float(val))
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
