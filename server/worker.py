from threading import Thread
import Queue
import time
from BeagleCommand.server import OutputSemaphore, QuitinTime, Debug

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
