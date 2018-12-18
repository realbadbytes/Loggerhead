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
            # Widen to $2 billion for now because hits are very low.
            if (latest_eps > 0) and (100000000 < marketcap <= 2000000000):
                multiple = (last_price / latest_eps)
                container['symbol'] = symbol
                container['marketcap'] = marketcap
                container['last_price'] = last_price
                container['multiple'] = multiple
                logger.success('Hit on {0}:{1}\n\t\t\t\t\t\t    Last price: {2}\n\t\t\t\t\t\t    Multiple: {3}' \
                        .format(name, symbol, last_price, multiple))
                hits.append(container)
        except IEXSymbolError as e:
            logger.error(str(e))
            continue
    return hits


def load_industry_syms(industry):
    industry_symbols = []
    with open('industry_data/'+industry+'.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            industry_symbols.append(row['Symbol'])
    return industry_symbols


def usage():
    print('Loggerhead v1.0\n\n\tusage: ./loggerhead.py [industry]\n\n\tAvailable industries:\n' \
            '\n\tbasic\tcapital_goods\tconsumer_durables\tconsumer_nondurables\n' \
            '\tconsumer_services\tenergy\t\tfinance\t\thealthcare\n' \
            '\tmisc\tpublic_utilities\ttechnology\ttransportation\n')


def main():
    coloredlogs.install(level='INFO')
    coloredlogs.increase_verbosity()

    if len(sys.argv) != 2:
        usage()
        exit(0)

    industry = sys.argv[1]
    industry_symbols = load_industry_syms(industry)
    logger.success('Loaded {0} symbols in the {1} industry.'.format(len(industry_symbols), industry))
    # Hit criteria is defined in the get_hits function temporarily
    hits = get_hits(industry_symbols)
    logger.success('Found {0} stock(s) of interest in the {1} industry.'.format(len(hits), industry))


if __name__ == '__main__':
    main()
