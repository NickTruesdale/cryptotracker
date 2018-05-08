import os
import csv
import datetime
import settings

from lib.portfolio import Portfolio, Inventory
from lib.exchange import Binance
from lib.currency import Currency, Pair


def generate_currency_file():

    binance = Binance(settings.APIKEY, settings.APISECRET)
    binance.connect()

    file = os.path.join(os.getcwd(), settings.CURRENCY_FILE)
    headers = ['coin', 'name', 'token']
    currencies = binance.get_currencies()

    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows([c, '', ''] for c in currencies)


def main():

    binance = Binance(settings.APIKEY, settings.APISECRET)
    binance.connect()
    binance.get_all_transactions()

    return binance


if __name__ == '__main__':
    main()
