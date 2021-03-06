from threading import Thread
import Queue
import time
import operator
import sys
import struct
import select
from BeagleCommand import OutputSemaphore, QuitinTime, Debug, pyserial

class Data(object):
    """Class to pass data around with"""
    pass

class Message(object):
    """Simple object to wrap interthread communication"""
    def __init__(self,to,msg):
        self.to = to
        self.msg = msg

class PacketException(Exception):
    """A general packet error"""
    def __init__(self, errstr):
        self.errstr = errstr

class PacketChecksumException(PacketException):
    """A packet with an invalid checksum has been received"""
    pass

class PacketLengthException(PacketException):
    """A packet with an invalid length has been received"""
    pass

class PacketCommandException(PacketException):
    """A packet with an invalid command has been received"""
    pass

class PacketValueException(PacketException):
    """A packet with an invalid value has been received"""
    pass

class Packet(object):
    """Simple object to wrap serial packets and verify them"""

    commands = {'\x00': 'time',
                '\x01': 'notime',
                '\x02': 'reboot',
                '\x03': 'poweroff',
                '\x04': 'get-time',
                '\x05': 'get-voltage',
                '\x06': 'get-used',
                '\x07': 'get-charged',
                '\x08': 'get-usedwhs',
                '\x09': 'get-chargedwhs',
                '\x0a': 'get-totalwhs',
                '\x0b': 'reply-time',
                '\x0c': 'reply-voltage',
                '\x0d': 'reply-used',
                '\x0e': 'reply-charged',
                '\x0f': 'reply-usedwhs',
                '\x10': 'reply-chargedwhs',
                '\x11': 'reply-totalwhs',
                '\x12': 'reset'
               }

    codes = {v:k for k,v in commands.iteritems()}

    def __init__(self, command=None, val=None, packetstr=None):
        if command:
            self.command = command
            self.val = val
        else:
            if len(packetstr) != 10:
                raise PacketLengthException(packetstr)
            if self.checksum(packetstr):
                try:
                    self.command, self.val = self.commands[packetstr[0]], self.unpack(packetstr[1:-1])
                except KeyError:
                    raise PacketCommandException(packetstr)
            else:
                raise PacketChecksumException(packetstr)

    def __str__(self):
        return self.checksumgen(self.codes[self.command]+self.pack(self.val))

    def pack(self,val):
        return struct.pack('d',val)

    def unpack(self, val):
        try:
            return struct.unpack('d',val)[0]
        except:
            raise PacketValueException(val)

    #http://code.activestate.com/recipes/52251/
    def checksumgen(self,s):
        """A simple packet checksum"""
        return s + chr(reduce(operator.add, map(ord, s)) % 256)

    def checksum(self,s):
        try:
            return s == self.checksumgen(s[:-1])
        except:
            return False

class Worker(Thread):

    def __init__(self,InQueue,MessageBox):
        super(Worker, self).__init__()
        self.InQueue = InQueue
        self.MessageBox = MessageBox
        self.messageBound = False

    def run(self):
        """main worker loop"""
        self.output('started')
        self.buildUp()
        while True:
            # Check if main thread is ready to stop
            if QuitinTime.is_set():
                self.tearDown()
                self.output('Quitin\'')
                return
            # check for messages
            while True:
                try: 
                    msg = self.InQueue.get(block=self.messageBound,timeout=0.5)
                    if Debug:
                        self.output('received ' + str(msg))
                    exec('self.{0}(*{1})'.format(msg[0],msg[1:]))
                except Queue.Empty:
                    break
            if not self.messageBound:
                self.loop()

    def buildUp(self):
        """executed when worker first starts"""
        pass

    def tearDown(self):
        """executed right before worker quits"""
        pass

    def loop(self):
        """loop executed when not message bound"""
        time.sleep(0.1)

    def output(self,msg):
        """acquire lock on output screen and write to it"""
        OutputSemaphore.acquire()
        print '{0}: {1}'.format(self.__class__.__name__, msg)
        OutputSemaphore.release()

    def reconnectSerial(self):
        """Reconnect to the serial port if something happens"""
        self.output('Closing Serial Port: ' + self.port)
        self.serial.flush()
        self.serial.close()
        time.sleep(5)
        self.output('Reopening Serial Port: ' + self.port)
        self.serial = pyserial.Serial(self.port, 19200)
        self.serial.timeout = 0.5

    def readline(self):
        """Read in 10-byte packet"""
        packetstr = []
        while len(packetstr) != 10:
            try:
                s = self.serial.read(1)
            except pyserial.SerialException:
                self.output('Serial Connection Error') 
                self.reconnectSerial()
                break
            packetstr.append(s)
            if s == '':
                break
        return ''.join(packetstr)

    def readSerial(self):
        if select.select([self.serial],[],[],0.5)[0]:
            try:
                packetstr = self.readline()
                p = Packet(packetstr=packetstr)
                if Debug:
                    self.output('Got Packet: Command: {0}, Value: {1}'.format(p.command, repr(p.val)))
                if '-' in p.command:
                    command, typestr = p.command.split('-')
                    exec('self.{0}(\'{1}\',\'{2}\')'.format(command, typestr, p.val))
                else:
                    exec('self.{0}(\'{1}\')'.format(p.command, p.val))
            except PacketException as e:
                if Debug:
                    self.output('{0}: {1}'.format(e.__class__.__name__, repr(e.errstr)))

    def send(self, command, val):
        """Send serial packet."""
        p = Packet(command, val)
        if Debug:
            self.output('Serial Out Packet: ' + repr(str(p)))
        try:
            self.serial.write(str(p))
        except pyserial.SerialException:
                self.output('Serial Connection Error') 
                self.reconnectSerial()
                return
        self.serial.flush()

