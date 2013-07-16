import signal, os
from Queue import Empty
from multiprocessing import Process, Queue
from BeagleCommand import QuitinTime

# create message passing queues
SerialIn = Queue()
StorageIn = Queue()
MessageBox = Queue()

QueueOwners = {'serial':SerialIn,'storage':StorageIn}

# wait until objects are defined to initialize workers
from storage import Storage
from serial import Serial

def run():
    """Run main server loop"""

    # create signal handler
    def signal_handler(sig, frame):
        print '\nCaught signal {0}... Quitin\' Time!'.format(str(sig))
        flaskProcess.terminate()
        flaskProcess.join()
        QuitinTime.set()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # create and start worker threads
    StorageThread = Storage(StorageIn,MessageBox)
    SerialThread = Serial(SerialIn,MessageBox)

    StorageThread.start()
    SerialThread.start()

    # start web server
    def f(MessageBox):
        from web import app
        app.MessageBox = MessageBox
        try:
            app.run(debug=True, use_reloader=False)
        except AttributeError:
            pass

    flaskProcess = Process(target=f, args=[MessageBox]) 
    flaskProcess.start()

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
        except Empty:
            pass
        except IOError:
            pass
