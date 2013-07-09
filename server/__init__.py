import signal
from threading import Thread, Semaphore, Event
import Queue

# show extra debug messages
Debug = True

# create semaphore so only one thread can output at a time
OutputSemaphore = Semaphore()

# create event to signal threads to stop
QuitinTime = Event()

# create event for time update
TimeUpdated = Event()

# create message passing queues
AcquireIn = Queue.Queue()
SerialIn = Queue.Queue()
StorageIn = Queue.Queue()
MessageBox = Queue.Queue()

QueueOwners = {'acquire':AcquireIn,'serial':SerialIn,'storage':StorageIn}

# wait until objects are defined to initialize workers
from acquire import Acquire
from storage import Storage
from serial import Serial

def run():
    """Run main server loop"""

    # create signal handler
    def signal_handler(sig, frame):
        print '\nCaught signal {0}... Quitin\' Time!'.format(str(sig))
        QuitinTime.set()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # create and start worker threads
    AcquireThread = Acquire(AcquireIn,MessageBox)
    StorageThread = Storage(StorageIn,MessageBox)
    SerialThread = Serial(SerialIn,MessageBox)

    AcquireThread.start()
    StorageThread.start()
    SerialThread.start()

    # pass messages until program is ended
    while True:
        # check to see if it's time to quit
        if QuitinTime.is_set():
            break
        try:
            # use timeout so that main thread can catch signals
            msg = MessageBox.get(timeout=0.5)
            for owner in msg.to:
                QueueOwners[owner].put(msg.msg)
        except Queue.Empty:
            pass

if __name__ == '__main__':
    run()
