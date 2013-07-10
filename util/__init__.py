import operator

class Message(object):
    """Simple object to wrap interthread communication"""
    def __init__(self,to,msg):
        self.to = to
        self.msg = msg

#http://code.activestate.com/recipes/52251/
def checksumgen(s):
    """A simple packet checksum"""
    return '{0}\0{1}\n'.format(s,reduce(operator.add, map(ord, s)) % 256)

def checksum(s):
    try:
        return s == checksumgen('\0'.join(s.split('\0')[0:2]))
    except:
        return False
