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
        # Filter by cramer's recommended "improperly handicapped" zone of $100 to $400 million
        # Widen to $2 billion for now because hits are very low.
        if (latest_eps > 0) and (100000000 < marketcap <= 2000000000):
            multiple = (last_price / latest_eps)
            container['symbol'] = symbol
            container['marketcap'] = marketcap
            container['last_price'] = last_price
            container['multiple'] = multiple
            logger.success('Hit on {0}:{1}\nLast price: {2}\nMultiple: {3}'.format(name, symbol, last_price, multiple))
            hits.append(container)
    return hits


def usage():
    print('Loggerhead v1.0\n\n\tusage: ./loggerhead.py [industry]\n\n\tAvailable industries:\n' \
            '\n\tbasic\tcapital_goods\tconsumer_durables\tconsumer_nondurables\n' \
            '\tconsumer_services\ttenergy\tfinance\thealthcare\n' \
            '\tmisc\tpublic_utilities\ttechnology\ttransportation\n')


def main():
    if len(sys.argv) != 2:
        usage()
        exit(0)

    industry = sys.argv[1]
    coloredlogs.install(level='INFO')
    coloredlogs.increase_verbosity()
    hits = process_symbols(NYSE_HEALTHCARE, industry)
    logger.success('Found {0} stock(s) of interest in the {1} industry.'.format(len(hits), industry))


if __name__ == '__main__':
    main()
