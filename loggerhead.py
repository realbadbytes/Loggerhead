#!/usr/bin/python3


from __future__ import print_function
import intrinio_sdk
import time
from intrinio_sdk.rest import ApiException
from pprint import pprint
from industries import NYSE_HEALTHCARE


intrinio_sdk.ApiClient().configuration.api_key['api_key'] = 'OjA3M2JmZjJkZWIxMDhjNTE0YTc5OTgwMDdlNGM5NDkx'
company_api = intrinio_sdk.CompanyApi()


def get_data(industry_list):
    for symbol in industry_list:
        # Filter by companies that have positive EPS
        try:
            eps = company_api.get_company_data_point_number(symbol, tag='basiceps')
            if eps > 0:
                #print('Positive EPS on {}'.format(symbol))
                mktcap = company_api.get_company_data_point_number(symbol, tag='marketcap')

                # We target mkt cap of $100 to $400 million
                if 100000000 < mktcap < 2000000000:
                    print('Positive EPS and target mkt cap range on {}'.format(symbol))
                    #lastprice = company_api.get_company_data_point_number(symbol, tag='last_price')
                    multiple = company_api.get_company_data_point_number(symbol, tag='pricetoearnings')
                    #evtoebitda = company_api.get_company_data_point_number(symbol, tag='evtoebitda')
                    epsgrowth = company_api.get_company_data_point_number(symbol, tag='epsgrowth')
                    print('{} @ multiple {}'.format(symbol, multiple))

        except ApiException as e:
            #print('ApiException on {}'.format(symbol))
            continue


def main():
    get_data(NYSE_HEALTHCARE)


if __name__ == '__main__':
    main()
