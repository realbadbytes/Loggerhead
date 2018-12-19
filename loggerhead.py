#!/usr/bin/python3
# https://iextrading.com/developer/docs
# https://addisonlynch.github.io/iexfinance/stable/stocks.html#key-stats

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


def cramer_micro_cap(symbols):
    """ Query the API and filter results based on market cap between $100-$400 million and positive EPS.

    :param symbols: List of stock symbols from a particular industry.
    :returns: List of stock symbols matching the criteria.
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
            logger.error(str(e) + '\n')
            continue

    return hits


def cramer_micro_cap(symbols):
    """ Query the API and filter results based on market cap between $100 million to $2 billion and positive EPS.

    :param symbols: List of stock symbols from a particular industry.
    :returns: List of stock symbols matching the criteria.
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

            if (latest_eps > 0) and (100000000 < marketcap <= 2000000000):
                multiple = (last_price / latest_eps)
                container['symbol'] = symbol
                container['marketcap'] = marketcap
                container['last_price'] = last_price
                container['multiple'] = multiple
                logger.success('Hit on {0}:{1}\n\t\t\t\t\t\t    Last price: {2}\n\t\t\t\t\t\t    Multiple: {3}\n' \
                        .format(name, symbol, last_price, multiple))
                hits.append(container)

        except IEXSymbolError as e:
            logger.error(str(e) + '\n')
            continue

    return hits



def large_trades_1pcnt(symbols):
    """ Query the API and filter results based on large trades greater than 1% of shares outstanding.

    :param symbols: List of stock symbols from a particular industry.
    :returns: List of stock symbols matching the criteria.
    """
    hits = []
    for symbol in symbols:
        container = {}
        try:
            stock = Stock(symbol)
            largest_trades = stock.get_largest_trades()
            shares_outstanding = stock.get_key_stats()['sharesOutstanding']
            if len(largest_trades) != 0 and shares_outstanding > 0:
                largest_trade = largest_trades[0]['size']
                trader = largest_trades[0]['venueName']
                # Is it a hedge fund sized move? Need to refine based on mkt cap and share price. The numbers here are for testing
                magnitude = (largest_trade / shares_outstanding)
                logger.info('{0} largest trade {1}, magnitude {2:.2%}'.format(symbol, largest_trade, magnitude))
                if magnitude > .005:
                    container['symbol'] = symbol
                    container['largest_trade'] = largest_trade
                    container['shares_outstanding'] = shares_outstanding
                    container['magnitude'] = magnitude
                    container['trader'] = trader
                    logger.success('Hit on {0}:\n\t\t\t\t\t\t    Shares outstanding: {1}\n\t\t\t\t\t\t    Largest trade: {2}\n' \
                            '\t\t\t\t\t\t    Magnitude: {3}\n\t\t\t\t\t\t    Executed by: {4}\n'
                            .format(symbol, shares_outstanding, largest_trade, magnitude, trader))
                    hits.append(container)

        except IEXSymbolError as e:
            logger.error(str(e) + '\n')
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
    print('Loggerhead v1.0\n\n\tusage: ./loggerhead.py [industry] [filter]\n\n\tAvailable industries:\n' \
            '\n\t\tbasic_industries\n\t\tcapital_goods\n\t\tconsumer_durables\n\t\tconsumer_nondurables\t\t' \
            '\n\t\tconsumer_services\n\t\tenergy\n\t\tfinance\n\t\thealthcare\t\t' \
            '\n\t\tmisc\n\t\tpublic_utilities\n\t\ttechnology\n\t\ttransportation\n' \
            '\n\tAvailable filters:\n \n\t\t1 - Cramer\'s $100-$400 million market cap and positive EPS\n' \
            '\t\t2 - Cramer\'s $100 mil to $2 billion market cap and positive EPS\n' \
            '\t\t3 - Large trades greater than .5% of the common stock\n')


def main():
    hits = []
    coloredlogs.install(level='INFO')
    coloredlogs.increase_verbosity()

    if len(sys.argv) != 3:
        usage()
        exit(0)

    # Prepare industry symbols
    industry = sys.argv[1]
    industry_symbols = load_industry_syms(industry)
    logger.info('Loaded {0} symbols in {1}\n'.format(len(industry_symbols), industry))

    # Run selected filter
    algo = int(sys.argv[2])
    if algo == 1:
        hits = cramer_micro_cap(industry_symbols)
    elif algo == 2:
        hits = cramer_small_cap(industry_symbols)
    elif algo == 3:
        hits = large_trades_1pcnt(industry_symbols)

    logger.info('Found {0} stock(s) of interest in {1}\n'.format(len(hits), industry))


if __name__ == '__main__':
    main()
