import time
import Adafruit_BBIO.ADC as ADC
from BeagleCommand import QuitinTime, TimeUpdated
from BeagleCommand.util import Worker, Message

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
        v = list()
        ua = list()
        ca = list()
        for x in range(0,100):
            v.append(ADC.read_raw('AIN1'))
            ua.append(ADC.read_raw('AIN2'))
            ca.append(ADC.read_raw('AIN3'))
            time.sleep(0.01)
        finish = time.time()
        d = finish - start
        t = start + d/2
        m = Message(to=['storage'],msg=['put', [t, d,
            self.mapVoltage(sum(v)/100), self.mapUsed(sum(ua)/100),
            self.mapCharged(sum(ca)/100)]])
        self.MessageBox.put(m)

    def mapVoltage(self,v):
        return 0.04897580239701511*v+0.07516742524744302

    def mapUsed(self,ua):
        v = 0.020815852896545563*ua -17.427836293849857
        return v*20

    def mapCharged(self,ca):
        v = 0.02053496737093381*ca-17.132253271999488
        return v*2.5
