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
    """ Query the API and process results based on market cap between $100-$400 million and positive EPS.

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
            logger.notice('{0} - Market cap {1}, Latest EPS {2}'.format(symbol, marketcap, latest_eps))

            if (latest_eps > 0) and (100000000 < marketcap <= 400000000):
                multiple = (last_price / latest_eps)
                container['symbol'] = symbol
                container['marketcap'] = marketcap
                container['last_price'] = last_price
                container['multiple'] = multiple
                logger.success('Hit on {0}:{1}\n\t\t\t\t       Last price: ${2}\n\t\t\t\t       Multiple: {3}' \
                        .format(name, symbol, last_price, multiple))
                hits.append(container)

        except IEXSymbolError as e:
            logger.error(str(e))
            continue

    return hits


def cramer_small_cap(symbols):
    """ Query the API and process results based on market cap between $100 million to $2 billion and positive EPS.

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
            logger.notice('{0} - Market cap {1}, Latest EPS {2}'.format(symbol, marketcap, latest_eps))

            if (latest_eps > 0) and (100000000 < marketcap <= 2000000000):
                multiple = (last_price / latest_eps)
                container['symbol'] = symbol
                container['name'] = name
                container['marketcap'] = marketcap
                container['last_price'] = last_price
                container['multiple'] = multiple
                logger.success('Hit on {0}:{1}\n\t\t\t\t       Last price: ${2}\n\t\t\t\t       Multiple: {3}' \
                        .format(name, symbol, last_price, multiple))
                hits.append(container)

        except IEXSymbolError as e:
            logger.error(str(e))
            continue

    return hits



def large_trades_halfpcnt(symbols):
    """ Query the API and process results based on large trades greater than .5% of shares outstanding.

    :param symbols: List of stock symbols from a particular industry.
    :returns: List of stock symbols matching the criteria.
    """
    hits = []
    for symbol in symbols:
        container = {}
        try:
            stock = Stock(symbol)
            largest_trades = stock.get_largest_trades()
            key_stats = stock.get_key_stats()
            shares_outstanding = key_stats['sharesOutstanding']
            name = key_stats['companyName']
            if len(largest_trades) != 0 and shares_outstanding > 0:
                largest_trade = largest_trades[0]['size']
                trader = largest_trades[0]['venueName']
                # Is it a hedge fund sized move? Need to refine based on mkt cap and share price. The numbers here are for testing
                magnitude = (largest_trade / shares_outstanding)
                logger.notice('{0} - largest trade {1} shares, magnitude {2:.2%}'.format(symbol, largest_trade, magnitude))
                if magnitude > .005:
                    container['symbol'] = symbol
                    container['largest_trade'] = largest_trade
                    container['name'] = name
                    container['shares_outstanding'] = shares_outstanding
                    container['magnitude'] = magnitude
                    container['trader'] = trader
                    logger.success('Hit on {0}:\n\t\t\t\t       Shares outstanding: {1}\n\t\t\t\t       Largest trade: {2}' \
                            '\n\t\t\t\t       Magnitude: {3:.2%}\n\t\t\t\t       Executed by: {4}'
                            .format(symbol, shares_outstanding, largest_trade, magnitude, trader))
                    hits.append(container)

        except IEXSymbolError as e:
            logger.error(str(e))
            continue

    return hits

def lowest_buzz_highest_eps(symbols):
    """ Query the API and process results based on positive EPS, high positive EPS surprise % (> 100%), 
        low news buzz in past 50 days (<= 1 story), zero debt, and a short ratio below 10%.
        This should indicate that people don't really know whats going on in the company and/or analysts
        dont have all the information. This stock could be improperly handicapped and present a nice opportunity.

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
            latest_eps = key_stats['latestEPS']
            eps_surprise_pcnt = key_stats['EPSSurprisePercent']
            news_buzz = stock.get_news(range=50)
            debt = key_stats['debt']
            short_ratio = key_stats['shortRatio']
            logger.notice('{0} - {1} news stories EPS surprise {2:.2%}, and latest EPS {3}'
                    .format(symbol, len(news_buzz), eps_surprise_pcnt, latest_eps))
            if (len(news_buzz) <= 1) and (latest_eps > 0) and (eps_surprise_pcnt > 0) \
                    and (debt <= 0) and (short_ratio is not None) and (short_ratio < 10.0):
                container['symbol'] = symbol
                container['name'] = name
                logger.success('Hit on {0}:\n\t\t\t\t       EPS Surprise %: {1:.2%}\n\t\t\t\t' \
                        '       Latest EPS: ${2}\n\t\t\t\t       News stories: {3}' \
                        .format(symbol, eps_surprise_pcnt, latest_eps, len(news_buzz)))
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
    print('Loggerhead v1.0\n\n\tusage: ./loggerhead.py [industry] [filter]\n\n\tAvailable industries:\n' \
            '\n\t\tbasic_industries\n\t\tcapital_goods\n\t\tconsumer_durables\n\t\tconsumer_nondurables\t\t' \
            '\n\t\tconsumer_services\n\t\tenergy\n\t\tfinance\n\t\thealthcare\t\t' \
            '\n\t\tmisc\n\t\tpublic_utilities\n\t\ttechnology\n\t\ttransportation\n' \
            '\n\tAvailable queries:\n \n\t\t1 - Cramer\'s $100-$400 million market cap and positive EPS.\n' \
            '\t\t2 - Cramer\'s $100 mil to $2 billion market cap and positive EPS.\n' \
            '\t\t3 - Large trades greater than .5% of shares outstanding.\n' \
            '\t\t4 - Stocks with highest EPS, positive past EPS surprise percentage,\n'
                    '\t\t    very low news buzz, zero debt, and a short ratio less than 10%.\n')


def main():
    hits = []
    coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s', level='INFO')
    coloredlogs.increase_verbosity()

    if len(sys.argv) != 3:
        usage()
        exit(0)

    # Prepare industry symbols
    industry = sys.argv[1]
    industry_symbols = load_industry_syms(industry)
    logger.info('Loaded {0} symbols in {1}'.format(len(industry_symbols), industry))

    # Run selected query
    choice = int(sys.argv[2])
    if choice == 1:
        hits = cramer_micro_cap(industry_symbols)
    elif choice == 2:
        hits = cramer_small_cap(industry_symbols)
    elif choice == 3:
        hits = large_trades_halfpcnt(industry_symbols)
    elif choice == 4:
        hits = lowest_buzz_highest_eps(industry_symbols)

    logger.success('Found {0} stock(s) of interest in {1} industry.'.format(len(hits), industry))
    for hit in hits:
        print('{0} - {1}'.format(hit['symbol'], hit['name']))


if __name__ == '__main__':
    main()
