import time
from BeagleCommand.server import TimeUpdated, Debug
from worker import Worker
from message import Message

class Serial(Worker):

    def buildUp(self):
        TimeUpdated.set()
        m = Message(to=['storage'],msg=['get',1234])
        self.MessageBox.put(m)

    def send(self,ID,*args):
        if Debug:
            self.output('Serial Out ID: '+str(ID))
