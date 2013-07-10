from BeagleCommand import pyserial
from BeagleCommand.util import Packet
import datetime

def run():
    ser = pyserial.Serial('/dev/ttyUSB0', 19200)
    datestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ser.write(Packet(ID=1234, command='time', args=[datestr]))
    ser.flush()
