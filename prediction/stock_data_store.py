import collections

StockDataNode = collections.namedtuple('StockDataNode', ['timestamp', 'open', 'high', 'low', 'close', 'volume'])

class StockDataStore(object):

    def __init__(self):
        self.data = collections.defaultdict(list)
