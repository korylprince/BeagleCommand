from threading import Semaphore, Event
import Queue
from BeagleCommand import QuitinTime

# create message passing queues
SerialIn = Queue.Queue()
MessageBox = Queue.Queue()

from web import app

# wait until objects are defined to initialize workers
from serial import Serial

def run():
    """Run main server loop"""

    # create and start worker threads
    SerialThread = Serial(SerialIn, MessageBox)

    SerialThread.start()

    # start web server
    app.run(debug=True, use_reloader=False)

    QuitinTime.set()

if __name__ == '__main__':
    run()
