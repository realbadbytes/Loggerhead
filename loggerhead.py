#!/usr/bin/python3
# https://iextrading.com/developer/docs

import sys
import csv
import time
import logging
import coloredlogs
import verboselogs
from iexfinance.stocks import Stock
from iexfinance.utils.exceptions import IEXSymbolError


logger = verboselogs.VerboseLogger('Loggerhead')
endpoint = 'https://api.iextrading.com/1.0'


def get_hits(symbols):
    """ Query the API and filter results based on some condition

    :param symbols: List of stock symbols from a particular industry
    :returns: List of stock symbols matching our criteria
    """

    hits = []

    for symbol in symbols:
        container = {}

        try:
            stock = Stock(symbol)
            key_stats = stock.get_key_stats()
            name = key_stats['companyName']
            marketcap = key_stats['marketcap']
            latest_eps = key_stats['latestEPS']
            last_price = stock.get_price()

            # Filter by cramer's recommended "improperly handicapped" zone of $100 to $400 million
            if (latest_eps > 0) and (100000000 < marketcap <= 400000000):
                multiple = (last_price / latest_eps)
                container['symbol'] = symbol
                container['marketcap'] = marketcap
                container['last_price'] = last_price
                container['multiple'] = multiple
                logger.success('Hit on {0}:{1}\n\t\t\t\t\t\t    Last price: {2}\n\t\t\t\t\t\t    Multiple: {3}\n' \
                        .format(name, symbol, last_price, multiple))
                hits.append(container)

        except IEXSymbolError as e:
            logger.error(str(e))
            continue

    return hits


def load_industry_syms(industry):
    """ Parse all symbols from .csv file containing all stock symbols for a particular industry.

    :param industry: User-provided industry string
    :returns: List of symbols in a particular industry
    """
    industry_symbols = []
    with open('industry_data/'+industry+'.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            industry_symbols.append(row['Symbol'])
    return industry_symbols


def usage():
    print('Loggerhead v1.0\n\n\tusage: ./loggerhead.py [industry]\n\n\tAvailable industries:\n' \
            '\n\t\tbasic_industries\n\t\tcapital_goods\n\t\tconsumer_durables\n\t\tconsumer_nondurables\t\t' \
            '\n\t\tconsumer_services\n\t\tenergy\n\t\tfinance\n\t\thealthcare\t\t' \
            '\n\t\tmisc\n\t\tpublic_utilities\n\t\ttechnology\n\t\ttransportation\n')


def main():
    coloredlogs.install(level='INFO')
    coloredlogs.increase_verbosity()

    if len(sys.argv) != 2:
        usage()
        exit(0)

    industry = sys.argv[1]
    industry_symbols = load_industry_syms(industry)
    logger.info('Loaded {0} symbols in {1}\n'.format(len(industry_symbols), industry))
    hits = get_hits(industry_symbols)
    logger.info('Found {0} stock(s) of interest in {1}\n'.format(len(hits), industry))


if __name__ == '__main__':
    main()
