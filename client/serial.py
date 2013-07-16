import os, time
import select
from BeagleCommand import QuitinTime, Debug
from BeagleCommand.util import Worker, Message, Packet, PacketException
from BeagleCommand import pyserial

class Serial(Worker):

    def __init__(self, InQueue, MessageBox):
        super(Serial,self).__init__(InQueue,MessageBox)
        self.port = "/dev/ttyUSB0"
        
        # compile values into dict
        self.rowdict = dict()

    def buildUp(self):
        self.output('Opening Serial Port: ' + self.port)
        self.serial = pyserial.Serial(self.port, 19200)
        self.serial.timeout = 0.1 
        self.time(0.0)

    def tearDown(self):
        self.serial.flush()
        self.serial.close()

    def run(self):
        """main worker loop"""
        self.output('started')
        self.buildUp()
        while True:
            self.loop()

            # Check if main thread is ready to stop
            if QuitinTime.wait(5):
                self.tearDown()
                self.output('Quitin\'')
                return

    def loop(self):
        for col in ['time', 'voltage', 'usedAmps', 'chargedAmps', 'kwhs']:
            while True:
                if QuitinTime.is_set():
                    return
                self.send('get-'+col,0.0)
                self.get()
                if col in self.rowdict:
                    break
            time.sleep(0.1)
        r = self.rowdict
        m = Message(to = ['storage'], msg = ['put', [r['time'], r['voltage'],
            r['usedAmps'], r['chargedAmps'], r['kwhs']]])
        self.MessageBox.put(m)
        self.rowdict.clear()

    def get(self):
        if select.select([self.serial],[],[],0.2)[0]:
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

    def reply(self, typestr, val):
        """Put value into current row"""
        self.rowdict[typestr] = val 

    def time(self, val):
        """Get system time and send it to server"""
        t = time.time()
        self.output('Sending Time: ' + str(t))
        self.send('time',t)

    def notime(self, val):
        """Resend time"""
        self.time(val)

    def reboot(self, val):
        self.send('reboot', 0.0)

    def poweroff(self, val):
        self.send('poweroff', 0.0)
