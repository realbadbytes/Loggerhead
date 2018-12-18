#!/usr/bin/python3
# https://iextrading.com/developer/docs

import time
import coloredlogs
import verboselogs
import logging
from iexfinance.stocks import Stock
from time import sleep
from industries import NYSE_HEALTHCARE


logger = verboselogs.VerboseLogger('Loggerhead')
endpoint = 'https://api.iextrading.com/1.0'


def get_data(symbol_list, industry_name):
    logger.info('Pulling data for industry: {}'.format(industry_name))
    for symbol in symbol_list:
        stock = Stock(symbol)
        key_stats = stock.get_key_stats()
        name = key_stats['companyName']
        print(name)
        marketcap = key_stats['marketcap']
        latest_eps = key_stats['latestEPS']
        last_price = stock.get_price()
        if (latest_eps > 0) and (100000000 < marketcap <= 2000000000):
            multiple = (last_price / latest_eps)
            logger.success('Hit on {0}:{1}\nLast price: {2}\nMultiple: {3}'.format(name, symbol, last_price, multiple))


def main():
    coloredlogs.install(level='INFO')
    coloredlogs.increase_verbosity()
    get_data(NYSE_HEALTHCARE, 'healthcare')


if __name__ == '__main__':
    main()
