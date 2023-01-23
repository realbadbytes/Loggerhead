#!/usr/bin/python3
# https://iextrading.com/developer/docs
# https://addisonlynch.github.io/iexfinance/stable/stocks.html#key-stats

# https://www.nasdaq.com/market-activity/stocks/screener

import sys
import csv
import os
import time
import logging
import coloredlogs
import verboselogs
from iexfinance.stocks import Stock

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
            stock = Stock(symbol, token="sk_73515507495b4464b4125514056f63e0")
            key_stats = stock.get_key_stats()
            name = key_stats['companyName'].values[0]
            marketcap = key_stats['marketcap'].values[0]
            latest_eps = key_stats['ttmEPS'].values[0]
            last_price = stock.get_price().values[0]
            #logger.notice('{0} - Market cap {1}, Latest EPS {2}'.format(symbol, marketcap, latest_eps))

            if (latest_eps > 0) and (100000000 < marketcap <= 400000000):
                multiple = (last_price / latest_eps)
                container['symbol'] = symbol
                container['marketcap'] = marketcap
                container['last_price'] = last_price
                container['multiple'] = multiple
                logger.success('Hit on {0}:{1}\n\t\t\t\t       Last price: ${2}\n\t\t\t\t       Multiple: {3}' \
                        .format(name, symbol, last_price, multiple))
                hits.append(container)

        except  Exception as e:
            logger.error(str(e))
            continue

    return hits


def cramer_small_cap(symbols):
    """ Query the API and process results based on market cap between $100 million to $2 billion and positive EPS.

    :param symbols: List of stock symbols from a particular industry.
    :returns: List of stock symbols matching the criteria.
    """
    symbols = list(symbols.keys())
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


def load_data():
    """ Parse all symbols from .csv file containing all stock symbols for a particular industry.

    :param industry: User-provided industry string
    :returns: List of symbols in a particular industry
    """
    market_data = {}
    directory = os.fsencode('industry_data')
    for file in os.listdir(directory):
        with open('industry_data/' + file.decode('utf-8')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                market_data[row['Symbol']] = row
    return market_data

def main():
    hits = []
    coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s', level='INFO')
    coloredlogs.increase_verbosity()

    # Prepare industry symbols
    market_data = load_data()

    # Run selected query
    hits = cramer_micro_cap(market_data)
    #hits = cramer_small_cap(market_data)
    #hits = large_trades_halfpcnt(market_data)
    #hits = lowest_buzz_highest_eps(market_data)

    logger.success('Found {0} stock(s) of interest'.format(len(hits)))
    for hit in hits:
        print('{0} - {1}'.format(hit['symbol'], hit['name']))


if __name__ == '__main__':
    main()
