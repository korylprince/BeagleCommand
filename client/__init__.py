from threading import Semaphore, Event
from BeagleCommand import QuitinTime
from BeagleCommand.util import Data

d = Data()

def run():
    """Run main server loop"""

    #create serial interface
    from serial import Serial
    d.serial = Serial()

    # start web server
    from web import app
    app.run(debug=True, use_reloader=False)

    QuitinTime.set()

if __name__ == '__main__':
    run()
