class FTNError (Exception):
    pass

class InvalidPacket (FTNError):
    pass

class InvalidMessage (FTNError):
    pass

class InvalidAddress (FTNError):
    pass

class InvalidRoute (FTNError):
    '''An invalid route specification was encountered in a 
    route configuration file.'''
    pass

class EndOfData (FTNError):
    pass

