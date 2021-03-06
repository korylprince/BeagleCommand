from threading import Semaphore, Event

# show extra debug messages
Debug = True

# create semaphore so only one thread can output at a time
OutputSemaphore = Semaphore()

# create event to signal threads to stop
QuitinTime = Event()

# create events for reboot and poweroff
Reboot = Event()
PowerOff = Event()

# create event for time update
TimeUpdated = Event()

import serial as pyserial
import util
import client
try:
    import server
except ImportError:
    pass
