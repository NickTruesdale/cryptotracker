from lib.exchange import Exchange, Binance
from lib.currency import Pair, Currency


class Portfolio:
    """
    This is the highest level summary of our crypto assets. It holds all of the transaction
    history objects retrieved from exchanges, and allows us to query for inventory at either
    the current time, or historically, or as a data set.
    """

    def __init__(self, exchange_names):
        """ """
        self.exchanges = [Exchange(name) for name in exchange_names]

    def connectExchanges(self):
        """ For each exchange in this portfolio, connect a client to that exchange's API """
        self.clients = [exchange.connect() for exchange in self.exchanges]


class Inventory:
    """
    This is an overview of our coin portfolio. Here we provide an aggregate trade history,
    a balance overview, current worth, profit, etc.
    """

    def __init__(self, client):
        """ """
        self.client = client

    def getPairs(self):
        """ Scan the binance API for pairs we have traded in. """
        pairs = client.get_exchange_info
