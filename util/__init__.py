import operator

class Message(object):
    """Simple object to wrap interthread communication"""
    def __init__(self,to,msg):
        self.to = to
        self.msg = msg

class PacketException(Exception):
    """A packet with an invalid checksum has been received"""
    def __init__(self,packetstr):
        self.packetstr = packetstr

class Packet(object):
    """Simple object to wrap serial packets"""
    def __init(self, ID=None, command=None, args=None, packetstr=None):
        if ID:
            self.ID = ID
            self.command = command
            self.args = args
        else:
            if checksum(packetstr):
                self.ID, cmd, chksum = packetstr.split('\0')
                self.command = cmd.split(',')[0].strip()
                self.args = [x.strip() for x in cmd.split(',')]
            else:
                raise PacketException(packetstr)

    def __str__(self):
        return checksumgen('{0}\0{1},{2}'.format(self.ID,self.command,','.join(args)))

    #http://code.activestate.com/recipes/52251/
    def checksumgen(s):
        """A simple packet checksum"""
        return '{0}\0{1}\n'.format(s,reduce(operator.add, map(ord, s)) % 256)

    def checksum(s):
        try:
            return s == checksumgen('\0'.join(s.split('\0')[0:2]))
        except:
            return False
