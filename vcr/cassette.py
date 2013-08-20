'''The container for recorded requests and responses'''

import os
import tempfile
try:
    from collections import Counter, OrderedDict
except ImportError:
    from .compat.counter import Counter
    from .compat.ordereddict import OrderedDict

from mocket import Mocket, MocketEntry

# Internal imports
from .persist import load_cassette, save_cassette
from .utils import get_host_and_port

class Cassette(MocketEntry):

    def __init__(self, path):
        self._path = path
        self.data = OrderedDict()
        self.play_counts = Counter()

    # Unused; included for compatibility with Mocket
    location = (None, None)

    '''A container for recorded requests and responses'''
    @classmethod
    def load(cls, path):
        '''Load in the cassette stored at the provided path'''
        new_cassette = cls(path)
        try:
            requests, responses = load_cassette(path)
            for request, response in zip(requests, responses):
                new_cassette.append(request, response)
        except IOError:
            pass
        return new_cassette

    @property
    def play_count(self):
        return sum(self.play_counts.values())

    @property
    def requests(self):
        return self.data.keys()

    @property
    def responses(self):
        return self.data.values()

    def mark_played(self, request):
        '''
        Alert the cassette of a request that's been played
        '''
        self.play_counts[request] += 1

    def append(self, request, response):
        '''Add a request, response pair to this cassette'''
        self.data[request] = response

    def response_of(self, request):
        '''Find the response corresponding to a request'''
        return self.data[request]

    # For compatibility with Mocketize API...
    get_response = response_of

    def _save(self):
        save_cassette(self._path, self.requests, self.responses)

    def __str__(self):
        return "<Cassette containing {0} recorded response(s)>".format(len(self))

    def __len__(self):
        '''Return the number of request,response pairs stored in here'''
        return len(self.data)

    def __contains__(self, request):
        '''Return whether or not a request has been stored'''
        return request in self.data

    def __enter__(self):
        # Register this casette with Mocket.
        for req in self.requests:
            Mocket._entries[get_host_and_port(req)].append(self)
        # Patch the real socket instance with a fake one.
        Mocket.enable()
        return self

    def __exit__(self, typ, value, traceback):
        for exchange in Mocket._record:
            self.append(exchange.request,
                        exchange.response)
        self._save()
        Mocket.disable()
        Mocket.reset()
