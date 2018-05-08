import os
import csv
import copy

from coinmarketcap import Market


class Pair:
    """
    The Binance API deals in trading pairs, so this is the most natural way to break up our data.
    For each pair, we want to specify transaction history (which gives balance over time) and
    historical price data.
    """

    def __init__(self, symbol, trade_symbol, base_symbol):
        """ """
        self.symbol = symbol
        
        try:
            self.trade_currency = CURRENCIES[CURRENCIES.index(trade_symbol)]
            self.base_currency = CURRENCIES[CURRENCIES.index(base_symbol)]
        except IndexError:
            raise Exception('Currency not recognized for pair: ' + symbol)

    def __eq__(self, pair):
        if isinstance(pair, Pair):
            return pair.symbol == self.symbol
        else:
            return pair == self.symbol

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return self.symbol

    def __lt__(self, pair):
        return self.symbol < pair.symbol


class Currency:
    """
    A simple class which represents a currency.
    """

    def __init__(self, symbol, name):
        """ """
        self.symbol = symbol
        self.name = name
        
        if self.symbol in ALIASES:
            self.alias = ALIASES[self.symbol]
        else:
            self.alias = self.symbol

    def __eq__(self, curr):
        if isinstance(curr, Currency):
            return curr.symbol == self.symbol
        else:
            return curr == self.symbol or curr == self.alias

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.name + ' (' + self.symbol + ')'

    def __repr__(self):
        return self.symbol


class Fiat(Currency):
    """
    This class inherits from Currency and adds specific fields/methods for Fiat currencies
    """

    def __init__(self, symbol, name):
        super().__init__(symbol, name)


class Coin(Currency):
    """
    This class inherits from Currency and adds a lot of statistics from Coinmarketcap
    """

    def __init__(self, data):
        """ Builds a cryptocurrency object using a dict from CoinMarketCap """
        for key in data:
            value = data[key]

            try:
                value = int(value)
            except (TypeError, ValueError):
                pass

            try:
                value = float(value)
            except (TypeError, ValueError):
                pass

            setattr(self, key, value)

        super().__init__(self.symbol, self.name)


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


ALIASES = {
    'YOYO': 'YOYOW',
    'IOTA': 'MIOTA',
    'BQX': 'ETHOS'
}

ALIASES.update({val: key for key, val in ALIASES.items()})


FIAT = [
    Fiat('USD', 'Dollar'),
    Fiat('GBP', 'British Pound'),
    Fiat('EUR', 'Euro')
]

# Module level variables
# CURRENCIES = load_from_csv()
COINS = CoinMarketCap().coins
CURRENCIES = FIAT + COINS

TRADE_CURRENCIES = [
    'EUR',
    'BTC',
    'ETH',
    'XRP',
    'LTC',
    'ADA',
    'XLM',
    'TRX',
    'MIOTA',
    'NEO',
    'XMR',
    'VEN',
    'BNB',
    'XVG',
    'NANO',
    'ONT',
    'WTC',
    'ICX'
]

TRADE_CURRENCIES = [copy.deepcopy(CURRENCIES[CURRENCIES.index(c)]) for c in TRADE_CURRENCIES]
