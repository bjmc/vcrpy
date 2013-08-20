from mocket import Mocket, MocketEntry

class Sockpuppet(Mocket):

    @classmethod
    def get_entry(cls, host, port, data):
        return cls._entries[0]
