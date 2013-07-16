import os, time
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
        self.serial.timeout = 0.5
        self.time(0.0)

    def tearDown(self):
        self.serial.flush()
        self.output('Closing Serial Port: ' + self.port)
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
                time.sleep(1.0)
                self.readSerial()
                if col in self.rowdict:
                    break
            time.sleep(0.1)
        r = self.rowdict
        m = Message(to = ['storage'], msg = ['put', [r['time'], r['voltage'],
            r['usedAmps'], r['chargedAmps'], r['kwhs']]])
        self.MessageBox.put(m)
        self.rowdict.clear()

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
