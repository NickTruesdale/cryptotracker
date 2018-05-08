from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException

from lib.currency import Currency, Pair, TRADE_CURRENCIES

from enum import Enum
from copy import copy, deepcopy
from time import time
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

import settings


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
        """ Initialize the Binance class with the API login info """
        self.api_key = api_key
        self.api_secret = api_secret

    def connect(self):
        """ Creates an instance of the Binance API client and populates general data """
        self.client = Client(self.api_key, self.api_secret)
        
        self.info = self.client.get_exchange_info()
        self.account = self.client.get_account()

        self.get_pairs()
        self.get_balances()

    def disconnect(self):
        """ Removes the instance of the Binance API client so it can be garbage collected """
        self.client = None

    def get_pairs(self):
        """ Get all of the pairs and currencies that Binance trades in """
        # Get all of the pairs that Binance trades in
        self.pairs = [Pair(pair['symbol'], pair['baseAsset'], pair['quoteAsset']) for pair in self.info['symbols']]
        self.pairs.append(Pair('BTCEUR', 'EUR', 'BTC'))
        self.pairs.append(Pair('ETHEUR', 'EUR', 'ETH'))

        # Get the list of unique currencies that Binance trades in
        self.currencies = [pair.trade_currency for pair in self.pairs] + [pair.base_currency for pair in self.pairs]
        self.currencies = list(set(self.currencies))

        # Initialize traded pairs with a guess
        pairs = []
        for coin in TRADE_CURRENCIES:
            pairs.append(coin.alias + 'BNB')
            pairs.append(coin.alias + 'ETH')
            pairs.append(coin.alias + 'BTC')

        self.traded_pairs = [self.pairs[self.pairs.index(p)] for p in pairs if p in self.pairs]

    def get_balances(self):
        """ Get the current balance for each currency in the static currency list """
        self.inventory = []
        for bal in self.account['balances']:
            symbol = bal['asset']
            amount = float(bal['free']) + float(bal['locked'])
            
            if (amount > 0 or symbol in TRADE_CURRENCIES) and (symbol in self.currencies):
                coin = deepcopy(self.currencies[self.currencies.index(symbol)])
                coin.amount = amount
                self.inventory.append(coin)

                if (symbol not in TRADE_CURRENCIES):
                    print('Non-zero balance for ' + symbol + ' not included in trade currencies!')

    def get_all_transactions(self):

        pool = ThreadPool(10)
        trades = pool.map(self.get_trade_history, self.traded_pairs)
        pool.close()
        pool.join()

        self.trades = [tx for txlist in trades for tx in txlist]
        self.transfers = self.get_transfer_history()

        self.txlist = self.trades + self.transfers
        self.txlist.sort()

        self.traded_pairs = list(set([tx.pair for tx in self.trades]))
        self.traded_pairs.sort()

    def get_trade_history(self, pair):
        """ """
        def create_transaction(trade):
            time = trade['time']

            buysign = 1.0 if trade['isBuyer'] else -1.0
            txtype = 'buy' if trade['isBuyer'] else 'sell'

            base_amount = Amount(-buysign * float(trade['qty']) * float(trade['price']), pair.base_currency)
            trade_amount = Amount(buysign * float(trade['qty']), pair.trade_currency)

            fee_currency = self.currencies[self.currencies.index(trade['commissionAsset'])]
            fee_amount = Amount(-float(trade['commission']), fee_currency)

            amounts = [trade_amount, base_amount, fee_amount]
            return Transaction(pair=pair, time=time, amounts=amounts, txtype=txtype)

        print('Trade history for: ' + str(pair))
        trades = self.client.get_my_trades(symbol=pair.symbol)
        return [create_transaction(trade) for trade in trades]

    def get_transfer_history(self):
        """  """
        def create_transaction(deposit):
            coin = self.currencies[self.currencies.index(deposit['asset'])]
            pair = self.pairs[self.pairs.index(deposit['asset'] + 'EUR')]

            time = deposit['insertTime']
            amount = deposit['amount']

            return Transaction(pair=pair, time=time, amounts=[Amount(amount, coin)], txtype='deposit')

        deposits = self.client.get_deposit_history()['depositList']
        return [create_transaction(deposit) for deposit in deposits]


class Transaction():
    """
    A simple object to represent transactions in trading history. Stores the time of the transaction,
    the amount gained, amount spent and fees paid.
    """
    TxTypes = Enum('TxTypes', ['withdrawal', 'deposit', 'buy', 'sell', 'cummulative', 'unknown'])

    def __init__(self, pair, time, amounts, txtype=None):
        # Pair
        self.pair = pair

        # Time (datetime format)
        self.time = time
        if (not isinstance(self.time, datetime)):
            self.time = datetime.fromtimestamp(int(self.time) / 1000)

        # Amounts
        self.amounts = amounts

        # Transaction type
        try:
            self.txtype = self.TxTypes[txtype]
        except KeyError:
            self.txtype = self.TxTypes.unknown

    def __str__(self):
        return '{0} {1} [{2}]: {3}'.format(str(self.pair), str(self.time), str(self.amounts), str(self.txtype))

    def __repr__(self):
        return 'Transaction({0}, {1}, {2}, {3})'.format(repr(self.pair), repr(self.time), repr(self.amounts), repr(self.txtype))

    def __add__(self, tx):
        """ Add the amounts of two transactions together """
        
        if not isinstance(tx, Transaction):
            tx = Transaction(self.pair, self.time, [], self.txtype.name)

        pair = self.pair if (self.pair == tx.pair) else None
        time = max(self.time, tx.time)
        txtype = self.txtype if (self.txtype == tx.txtype) else self.TxTypes.cummulative
        amounts = self.amounts + tx.amounts

        return Transaction(pair, time, amounts, txtype.name)

    def __radd__(self, tx):
        return self + tx

    def __lt__(self, tx):
        return self.time < tx.time

    def mergeAmounts(self):
        """ Merge amounts that share the same currency into one """
        currencies = set([amount.currency for amount in self.amounts])
        amountLists = [[a for a in self.amounts if a.currency == c] for c in currencies]

        self.amounts = [sum(a) for a in amountLists]


class Amount():
    """
    An even simpler object that is really just a named tuple for an amount and currency
    """

    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return str(self.currency) + ': ' + str(self.amount)

    def __repr__(self):
        return 'Amount(' + repr(self.currency) + ', ' + repr(self.amount) + ')'

    def __add__(self, a):
        if isinstance(a, Amount) and a.currency != self.currency:
            raise Exception('Cannot add two amounts with different currencies: ' + str(self.currency) + ', ' + str(a.currency))
        else:
            return Amount(self.amount + float(a), self.currency)

    def __radd__(self, a):
        return self + a

    def __float__(self):
        return self.amount


def test():
    b = Binance(settings.APIKEY, settings.APISECRET)
    b.connect()
    b.get_all_transactions()

    return b


b = test()
