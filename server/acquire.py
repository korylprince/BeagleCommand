import time
import Adafruit_BBIO.ADC as ADC
from BeagleCommand import QuitinTime, TimeUpdated
from BeagleCommand.util import Worker

class Acquire(Worker):

    def buildUp(self):
        self.output('Waiting for time to update...')
        # wait for time to come
        while not TimeUpdated.is_set() and not QuitinTime.is_set():
            TimeUpdated.wait(0.5)
        else:
            # if time never came and it's time to quit, skip tear down
            if QuitinTime.is_set():
                self.tearDown = lambda : None
                return
        self.output('Time updated... Starting')
        
        # setup sensors
        ADC.setup()

    def run(self):
        self.output('started')
        self.buildUp()
        while True:
            # Check if main thread is ready to stop
            if QuitinTime.is_set():
                self.tearDown()
                self.output('Quitin\'')
                return
            self.loop()

    def loop(self):
        start = time.time()
        for x in range(0,100):
            v = list()
            ua = list()
            ca = list()
            v.append(ADC.read_raw('AIN1'))
            ua.append(ADC.read_raw('AIN2'))
            ca.append(ADC.read_raw('AIN3'))
            time.sleep(0.01)
        finish = time.time()
        d = finish - start
        t = start + d/2
        m = Message(to=['storage'],msg=['put', t, d,
            self.mapVoltage(sum(v)/100), self.mapUsedAmps(sum(ua)/100),
            self.mapChargedAmps(sum(ca)/100)])
        self.MessageBox.put(m)

    def mapVoltage(self,v):
        return v

    def mapUsedAmps(self,ua):
        return ua

    def mapChargedAmps(self,ca):
        return ca
