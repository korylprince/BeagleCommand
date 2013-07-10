from BeagleCommand import pyserial
from BeagleCommand.util import checksumgen, checksum
import datetime

def run():
    ser = pyserial.Serial('/dev/ttyUSB0', 19200)
    datestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ser.write(checksumgen('1234\0time.'+datestr))
    ser.flush()
    

