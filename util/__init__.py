import operator

class Message(object):
    """Simple object to wrap interthread communication"""
    def __init__(self,to,msg):
        self.to = to
        self.msg = msg

#http://code.activestate.com/recipes/52251/
def checksumgen(s):
    """A simple packet checksum"""
    return reduce(operator.add, map(ord, s)) % 256
