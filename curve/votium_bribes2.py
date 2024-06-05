from ScanApi.scan_api import ScanApi
from ScanApi.info import eth_infura, API_KEY_ETHER_SCAN
from ScanApi.utils.functions import timestamp_to_date, convert_date_to_timestamp
import json
from web3 import Web3
import pandas as pd
from get_price_moralis import get_price_moralis
from openpyxl import Workbook
from eth_abi import decode

ether_scan = ScanApi(rpc=eth_infura, chain='ETH', api_key=API_KEY_ETHER_SCAN)
votium_bribe_address = '0x63942E31E98f1833A234077f47880A66136a2D1e'
votium_bribe_abi = ether_scan.get_contract_abi(votium_bribe_address)
votium_bribe_contract = ether_scan.get_contract(contract_address=votium_bribe_address, abi=votium_bribe_abi)

START_TIMESTAMP_ROUND1 = 1630951200
EPOCH_DURATION = 86400 * 14 # 2 weeks
roundDuration = 86400 * 5; # 5 days
deadlineDuration = 60 * 60 * 6; # 6 hours


def calculate_round(timestamp):
    return int(((timestamp - START_TIMESTAMP_ROUND1) / EPOCH_DURATION) + 1)


def get_bribes(round_number):
    date_start_timestamp = START_TIMESTAMP_ROUND1 + EPOCH_DURATION * round_number 
    date_end_timestamp = date_start_timestamp + EPOCH_DURATION

    start_block = ether_scan.get_block_number_by_timestamp(date_start_timestamp, 'before')
    try:
        end_block = ether_scan.get_block_number_by_timestamp(date_end_timestamp, 'before')
    except:
        end_block = eth_infura.eth.get_block_number()

    for log in ether_scan.get_logs(votium_bribe_address, '0x7c0c0ef7f1ccead819631ed9c10b0728e76274ee5572b53716ea96e7ec735ffa', start_block, end_block):

        transaction_hash = log['transactionHash']
        block_number = Web3.to_int(hexstr=log['blockNumber'])

        timestamp = ether_scan.get_timestamp(transaction_hash)
        date = timestamp_to_date(int(timestamp))

        binary_event_log = eth_infura.to_bytes(hexstr=log['data'])
        topics = log['topics']
        round = Web3.to_int(hexstr=topics[1])
        gauge_address = "0x" + topics[2][26:]
        briber = "0x" + topics[3][26:]

        try:
            input_decoded = decode(['(uint256,address,uint256,uint256,address[],bool)'], binary_event_log)[0]
        except Exception as e:
            print(e)
            token_name = 'ERROR'
            token_address = 'ERROR'
            amount = 'ERROR'
        else:
            token_address = input_decoded[1]
            amount = input_decoded[2]

            token_name = ether_scan.get_token_symbol(token_address)
            token_decimals = int(ether_scan.get_token_decimals(token_address))
                
            
            amount = amount / 10**token_decimals

            # try:
            #     token_price = get_price_moralis('eth', token_address, block_number)['usdPrice']
            #     amount_dollar = amount * float(token_price)
            # except:
            #     token_price = 'ERROR'
            #     amount_dollar = 'ERROR'

            token_price = ''
            amount_dollar = ''
            print({'Date': date, 'Round': round, 'Token name': token_name, 'Token address': token_address, 'Token amount': amount, 'Token price': token_price, 'Amount $': amount_dollar, 'Gauge': gauge_address, 'Briber': briber, 'Timestamp': timestamp, 'Block Number': block_number, 'Tx hash': transaction_hash})
            yield date, round, token_name, token_address, amount, token_price, amount_dollar, gauge_address, briber, timestamp, block_number, transaction_hash



def create_sheet(round_number):
    wb = Workbook()
    ws = wb.active
    ws.append(['Date', 'Round', 'Token Name', 'Token Address', 'Token Amount', 'Token Price', 'Amount $', 'Gauge', 'Briber', 'Timestamp', 'Block Number', 'Tx Hash'])
    

    for bribe in get_bribes(round_number-1):
        # print(bribe)
        ws.append(bribe)
    wb.save(f'Votium_Bribe_Round{round_number}.xlsx')
    #     df = df._append(bribe, ignore_index=True)
    
    # df.to_excel(file_path, index=False)

