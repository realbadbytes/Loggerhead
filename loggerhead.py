#!/usr/bin/python3
# https://iextrading.com/developer/docs

import sys
import time
import coloredlogs
import verboselogs
import logging
from iexfinance.stocks import Stock
from pprint import pprint
from time import sleep
from industries import NYSE_HEALTHCARE


logger = verboselogs.VerboseLogger('Loggerhead')
endpoint = 'https://api.iextrading.com/1.0'


def process_symbols(symbol_list, industry_name):
    hits = []
    logger.info('Pulling data for industry: {}'.format(industry_name))
    for symbol in symbol_list:
        container = {}
        stock = Stock(symbol)
        key_stats = stock.get_key_stats()
        name = key_stats['companyName']
        print(name)
        marketcap = key_stats['marketcap']
        latest_eps = key_stats['latestEPS']
        last_price = stock.get_price()
        if (latest_eps > 0) and (100000000 < marketcap <= 2000000000):
            multiple = (last_price / latest_eps)
            container['symbol'] = symbol
            container['marketcap'] = marketcap
            container['last_price'] = last_price
            container['multiple'] = multiple
            logger.success('Hit on {0}:{1}\nLast price: {2}\nMultiple: {3}'.format(name, symbol, last_price, multiple))
            hits.append(container)
    return hits


def main():
    industry = sys.argv[1]
    coloredlogs.install(level='INFO')
    coloredlogs.increase_verbosity()
    hits = process_symbols(NYSE_HEALTHCARE, industry)
    logger.success('Found {0} stocks of interest in {1} sector.'.format(len(hits), industry))


if __name__ == '__main__':
    main()
