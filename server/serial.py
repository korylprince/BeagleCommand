import time
from BeagleCommand.server import TimeUpdated
from worker import Worker

class Serial(Worker):

    def buildUp(self):
        TimeUpdated.set()
