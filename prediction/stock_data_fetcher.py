import quandl

# get the table for daily stock prices and,
# filter the table for selected tickers, columns within a time range
# set paginate to True because Quandl limits tables API to 10,000 rows per call

class Quandl(object):
    _FETCH_COLUMNS = ['ticker', 'date', 'open', 'close', 'high', 'low', 'volume']
    def __init__(self, apiKey):
        quandl.ApiConfig.api_key = apiKey

    def getStocks(self, tickers, startDay, endDay, outputPath):
        data = quandl.get_table('WIKI/PRICES',
                                ticker = tickers,
                                qopts = { 'columns':  self._FETCH_COLUMNS },
                                date = { 'gte': startDay, 'lte': endDay },
                                paginate=True)

        self._writeToCsv(data, outputPath)

    def _writeToCsv(self, data, outputPath):
        data.head()
