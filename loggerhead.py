#!/usr/bin/python3


from __future__ import print_function
import intrinio_sdk
import time
from intrinio_sdk.rest import ApiException
from pprint import pprint
from industries import HEALTHCARE


intrinio_sdk.ApiClient().configuration.api_key['api_key'] = 'OjA3M2JmZjJkZWIxMDhjNTE0YTc5OTgwMDdlNGM5NDkx'
company_api = intrinio_sdk.CompanyApi()


def get_data(industry_list):
    for symbol in industry_list:
        try:
            #mktcap = company_api.get_company_data_point_number(symbol, tag='marketcap')
            #lastprice = company_api.get_company_data_point_number(symbol, tag='last_price')
            multiple = company_api.get_company_data_point_number(symbol, tag='pricetoearnings')
            pprint('{} @ multiple {}'.format(symbol, multiple))
        except ApiException as e:
            print('ApiException on {}'.format(symbol))
            continue


def main():
    get_data(HEALTHCARE)


if __name__ == '__main__':
    main()
