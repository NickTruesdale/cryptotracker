from binance.client import Client
from lib.currency import Currency, Pair


class Exchange:
    """
    Presumably, we want to interface with multiple exchanges (Binance, GDAX, IDEX, etc.).
    This is a class that wraps each API and provides a common interface to the rest of our project.
    """

    def __init__(self):
        """ """
        pass


class Binance(Exchange):
    """
    This class extends the Exchange class and provides API-specific methods for Binance.
    """

    def __init__(self, api_key, api_secret):
        """ """
        Exchange.__init__(self)
        
        self.api_key = api_key
        self.api_secret = api_secret

    def connect(self):
        """ Creates an instance of the Binance API client """
        self.client = Client(self.api_key, self.api_secret)
        self.get_pairs()

    def disconnect(self):
        """ Removes the instance of the Binance API client so it can be garbage collected """
        self.client = None

    def get_pairs(self):
        """ Uses the exchange info object to search for all pairs with a trade history
        Note: This is currently very time intensive. There must be a better way...
        """
        symbols = self.client.get_exchange_info()['symbols']
        self.pairs = [Pair(symbol['symbol'], symbol['baseAsset'], symbol['quoteAsset']) for symbol in symbols]

    def get_currencies(self):
        """ Lists all of the unique currencies that this exchange deals in """
        currencies = []
        for pair in self.pairs:
            currencies.append(pair.trade_currency.symbol)
            currencies.append(pair.base_currency.symbol)

        currencies = list(set(currencies))
        return currencies

    def get_trade_history(self):
        """ """
        if not self.pairs:
            self.get_pairs()
