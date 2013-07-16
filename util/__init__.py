from threading import Thread
import Queue
import time
import operator
import sys
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
    """A packet with an invalid checksum has been received"""
    def __init__(self,packetstr):
        self.packetstr = repr(packetstr)

class Packet(object):
    """Simple object to wrap serial packets and verify them"""
    def __init__(self, ID=None, command=None, args=None, packetstr=None):
        if ID:
            self.ID = ID
            self.command = command
            self.args = args
        else:
            if self.checksum(packetstr):
                self.ID, cmd, chksum = packetstr.split('^')
                self.command = cmd.split(',')[0].strip()
                self.args = [x.strip() for x in cmd.split(',')[1:]]
            else:
                raise PacketException(packetstr)

    def __str__(self):
        if self.args is None:
            return self.checksumgen('{0}^{1}'.format(self.ID,self.command,))
        else:
            return self.checksumgen('{0}^{1},{2}'.format(self.ID,self.command,','.join(self.args)))

    #http://code.activestate.com/recipes/52251/
    def checksumgen(self,s):
        """A simple packet checksum"""
        return '{0}^{1}\xff'.format(s,reduce(operator.add, map(ord, s)) % 256)

    def checksum(self,s):
        try:
            return s == self.checksumgen('^'.join(s.split('^')[0:2]))
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
        print '{0}: {1}'.format(self.__class__.__name__, repr(msg))
        OutputSemaphore.release()
