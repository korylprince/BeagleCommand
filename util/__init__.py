from threading import Thread
import Queue
import time
import operator
import sys
import struct
from BeagleCommand import OutputSemaphore, QuitinTime, Debug

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
                '\x06': 'get-usedAmps',
                '\x07': 'get-chargedAmps',
                '\x08': 'get-kwhs',
                '\x09': 'reply-time',
                '\x0a': 'reply-voltage',
                '\x0b': 'reply-usedAmps',
                '\x0c': 'reply-chargedAmps',
                '\x0d': 'reply-kwhs'
               }

    codes = {v:k for k,v in commands.iteritems()}

    def __init__(self, command=None, val=None, packetstr=None):
        if command:
            self.command = command
            self.val = val
        else:
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
        return struct.pack('f',val)

    def unpack(self, val):
        try:
            struct.unpack('f',val)
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
