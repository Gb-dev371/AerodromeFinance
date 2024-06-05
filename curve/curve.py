'''
round - gauge_address - pool_symbol - relative_weights - votes - daily_crv_emissions - dolar_value_emissions
'''

import requests
import pandas as pd
from get_price_moralis import get_price_moralis
from ScanApi.scan_api import ScanApi
from ScanApi.info import eth_infura, API_KEY_ETHER_SCAN
from decimal import Decimal

ether_scan = ScanApi(rpc=eth_infura, chain='ETH', api_key=API_KEY_ETHER_SCAN)
seconds_in_a_week = 604800
round1 = 1631664000
round1 = 1631059200

epochDuration = 86400 * 14 # 2 weeks
roundDuration = 86400 * 5; # 5 days
deadlineDuration = 60 * 60 * 6; # 6 hours

def current_epoch(timestamp):
    return (timestamp / epochDuration) * epochDuration


def calculate_round(timestamp):
    if(timestamp < current_epoch(timestamp) + roundDuration - deadlineDuration):
        return int(current_epoch(timestamp) / epochDuration - 1348)
    else:
        return int(current_epoch(timestamp) / epochDuration - 1347)

# print(calculate_round(1715979641))

INFLATION_RATE = 5181574864521283150 / 10**18 # per second

def get_all_gauges():
    url = 'https://api.curve.fi/v1/getAllGauges'

    response = requests.get(url)
    data = response.json()

    pools_data = data['data']

    return pools_data


def get_pools_data(pools_data):
    file = 'curve_gauge_data_2.xlsx'
    df = pd.read_excel(file)
    keys = pools_data.keys()
    for pool in keys:
        pool_dict = pools_data[pool]
        pool_name = pool_dict['shortName']
        gauge_address = pool_dict['gauge']
        gauge_controller_data = pool_dict['gauge_controller']
        gauge_relative_weight = int(gauge_controller_data['gauge_relative_weight']) / 10**18
        gauge_weight = int(gauge_controller_data['get_gauge_weight']) / 10**18

        crv_emissions_for_gauge_per_second = gauge_relative_weight * INFLATION_RATE

        # crv_price = get_historical_crv_price()
        line = {'Pool Name': pool_name, 'Gauge Address': gauge_address}
        df = df._append(line, ignore_index=True)
    df.to_excel(file, index=False)

        # dict = {'Pool Name': pool_name, 'Gauge Address': gauge_address, 'Gauge Relative Weight': gauge_relative_weight, 'Gauge Weight': gauge_weight, 'CRV Emissions for Gauge per Second': crv_emissions_for_gauge_per_second}
        # print(dict)
        # pool_name = pool_data
        # print(pool_name)
        # break


def get_historical_token_price(chain:str, address:str, interval:str, start_timestamp:int):
    """_summary_

    Args:
        chain (str): Chain name (ethereum, polygon, arbitrum, etc)
        address (str): Token address
        interval (str): day, hour, minute
        start_timestamp (int): timestamp to get token price

    Returns:
        data(str): token price
    """
    end_timestamp = int(start_timestamp) + 604800
    url = f'https://prices.curve.fi/v1/usd_price/{chain}/{address}/history?interval={interval}&start={start_timestamp}&end={end_timestamp}'

    response = requests.get(url)
    data = response.json()['data'][0]['price'] # to get only the first price
    return data


def get_gauge_weight_history(gauge_address):
    # file = 'curve_gauge_data.xlsx'
    # df = pd.read_excel(file)

    url = f'https://prices.curve.fi/v1/dao/gauges/{gauge_address}/weight_history'

    response = requests.get(url)

    data = response.json()['data']
    
    for item in data:
        
        try:
            gauge_weight = int(Decimal(item['gauge_weight'])) / 10**18
        except:
            gauge_weight = item['gauge_weight']
            print('ERROOOOOOOOOOR')
        gauge_relative_weight = int(Decimal(item['gauge_relative_weight'])) / 10**18
        emissions_per_week = float(item['emissions'])
        timestamp_start_votation = item['epoch']
        

        try:
            crv_price = float(get_price_moralis('eth', '0xD533a949740bb3306d119CC777fa900bA034cd52', ether_scan.get_block_number_by_timestamp(timestamp_start_votation, 'before'))['usdPrice'])
            # crv_price = float(get_historical_token_price('ethereum', '0xD533a949740bb3306d119CC777fa900bA034cd52', 'minute', timestamp_start_votation))
            dolar_value_emissions = emissions_per_week * crv_price
        except:
            crv_price = 'ERROR'
            dolar_value_emissions = 'ERROR'

        round = int((timestamp_start_votation - round1) / seconds_in_a_week)

        # line = {'Round': timestamp_start_votation, 'Gauge Address': gauge_address, 'Gauge Relative Weight': gauge_relative_weight, 'Votes Amount': gauge_weight, 'Emissions per week': emissions_per_week, 'Dolar Value Emissions': dolar_value_emissions, 'CRV Price': crv_price}
        yield [timestamp_start_votation, round, gauge_address, gauge_relative_weight, gauge_weight, emissions_per_week, dolar_value_emissions, crv_price]
        # df = df._append(line, ignore_index=True)
        
    # df.to_excel(file, index=False)
    


    

# print(get_historical_token_price('ethereum', '0xD533a949740bb3306d119CC777fa900bA034cd52', 'minute', '1648684800'))

# get_pools_data(get_all_gauges())

