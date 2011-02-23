class FTNError (Exception):
    pass

class InvalidPacket (FTNError):
    pass

class InvalidMessage (FTNError):
    pass

class EndOfData (FTNError):
    pass

