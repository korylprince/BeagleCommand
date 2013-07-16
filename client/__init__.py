from threading import Semaphore, Event
from BeagleCommand import QuitinTime

#create serial interface
from serial import Serial
ser = Serial()

from web import app

def run():
    """Run main server loop"""

    # start web server
    app.run(debug=True, use_reloader=False)

    QuitinTime.set()

if __name__ == '__main__':
    run()
