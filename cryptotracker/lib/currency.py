import os
import csv

from coinmarketcap import Market


class Pair:
    """
    The Binance API deals in trading pairs, so this is the most natural way to break up our data.
    For each pair, we want to specify transaction history (which gives balance over time) and
    historical price data.
    """

    def __init__(self, symbol, trade_currency, base_currency):
        """ """
        self.symbol = symbol
        self.base_currency = Currency(base_currency)
        self.trade_currency = Currency(trade_currency)


class Currency:
    """
    A simple class which represents a currency.
    """

    def __init__(self, symbol, name):
        """ """
        self.symbol = symbol
        self.name = name

    def __str__(self):
        return self.name + ' (' + self.symbol + ')'

    def __repr__(self):
        return self.name + ' (' + self.symbol + ')'


class Fiat(Currency):
    """
    This class inherits from Currency and adds specific fields/methods for Fiat currencies
    """


class Coin(Currency):
    """
    This class inherits from Currency and adds a lot of statistics from Coinmarketcap
    """

    def __init__(self, *data, **kwargs):
        """ Builds a cryptocurrency object using a dict from CoinMarketCap """
        for dictionary in data:
            for key in dictionary:
                setattr(self, key, dictionary[key])

        for key in kwargs:
            setattr(self, key, kwargs[key])


class CoinMarketCap:
    """
    Much like the exchange classes, this wraps the Coinmarketcap API so we can access data for all
    altcoins. This includes overall market price (not trade price) at the current moment.
    """

    def __init__(self):
        self.update()

    def update(self):
        market = Market()
        self.coins = [Coin(data) for data in market.ticker(limit=0)]


def load_from_coinmarketcap():
    """ Loads all coins listed on coinmarketcap and returns a list of Currency objects """
    market = Market()
    coins = market.ticker(limit=0)
    return [Currency(c['symbol'], c['name']) for c in coins]


# Load static list of currencies
def load_from_csv():
    """ Loads a list of Currency objects from CSV """
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'currencies.csv')
    currencies = []

    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            currencies.append(Currency(*row))

    return currencies


FIAT = [
    Fiat('USD', 'Dollar'),
    Fiat('GBP', 'British Pound')
    Fiat('EUR', 'Euro'),
]


# Module level variables
# CURRENCIES = load_from_csv()
COINS = load_from_coinmarketcap()
CURRENCIES = FIAT + COINS
