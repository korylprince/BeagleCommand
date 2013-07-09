class Message(object):
    """Simple object to wrap interthread communication"""
    def __init__(self,to,msg):
        self.to = to
        self.msg = msg
