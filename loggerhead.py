#!/usr/bin/python3


import intrinio_sdk
import time
import coloredlogs
import verboselogs
import logging
from intrinio_sdk.rest import ApiException
from industries import NYSE_HEALTHCARE


intrinio_sdk.ApiClient().configuration.api_key['api_key'] = 'OjA3M2JmZjJkZWIxMDhjNTE0YTc5OTgwMDdlNGM5NDkx'
company_api = intrinio_sdk.CompanyApi()
#logger = logging.getLogger('Loggerhead')
logger = verboselogs.VerboseLogger('Loggerhead')

def get_data(symbol_list, industry_name):
    logger.info('Pulling data for industry: {}'.format(industry_name))
    for symbol in symbol_list:
        try:
            eps = company_api.get_company_data_point_number(symbol, tag='basiceps')
            # Filter by companies that have positive EPS
            if eps > 0:
                mktcap = company_api.get_company_data_point_number(symbol, tag='marketcap')

                # We target mkt cap of $100 to $400 million
                if 100000000 < mktcap < 2000000000:
                    logger.success('Positive EPS and good market cap range for symbol {}'.format(symbol))
                    # Get relevant metrics for hit
                    lastprice = company_api.get_company_data_point_number(symbol, tag='last_price')
                    multiple = company_api.get_company_data_point_number(symbol, tag='pricetoearnings')
                    #evtoebitda = company_api.get_company_data_point_number(symbol, tag='evtoebitda')
                    #epsgrowth = company_api.get_company_data_point_number(symbol, tag='epsgrowth')
                    logger.success('{0}\nLast price: {1}\nMultiple: {2}\EV/EBITDA: {3}\nEPS Growth: {4}'.format(symbol, lastprice, evtoebitda, epsgrowth, multiple))

        except ApiException as e:
            logger.error('ApiException on {}: {}'.format(symbol, str(e)))
            continue


def main():
    coloredlogs.install(level='DEBUG')
    coloredlogs.increase_verbosity()
    get_data(NYSE_HEALTHCARE, 'healthcare')


if __name__ == '__main__':
    main()
