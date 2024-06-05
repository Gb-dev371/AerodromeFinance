from ScanApi.scan_api import ScanApi
from ScanApi.info import eth_infura, API_KEY_ETHER_SCAN
from ScanApi.utils.functions import timestamp_to_date, convert_date_to_timestamp
import json
from web3 import Web3
import pandas as pd
from curve.curve import get_historical_token_price
from get_price_moralis import get_price_moralis
from openpyxl import Workbook

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

        event_bribe = votium_bribe_contract.events.NewIncentive()
        receipt = eth_infura.eth.get_transaction_receipt(transaction_hash)
        decode = event_bribe.process_receipt(receipt) # tuple of dicts

        timestamp = ether_scan.get_timestamp(transaction_hash)
        date = timestamp_to_date(int(timestamp))

        '''
        each dict has: 'args': {'round', 'gauge', 'depositor', 'index', 'token', 'amount', 'maxPerVote', 'excluded', 'recycled'}, 'event', 'logIndex', 'transaxtionIndex', 'transactionHash', 'address', 'blockHash'
        '''
        for info in decode:

            tx_hash = Web3.to_hex(info['transactionHash'])
            timestamp = ether_scan.get_timestamp(transaction_hash)

            date = timestamp_to_date(timestamp)

            args = info['args']
            round = args['_round']
            gauge = args['_gauge']
            briber = args['_depositor']
            token_address = args['_token']
            amount = int(args['_amount'])

            
            token_name = ether_scan.get_token_symbol(token_address)
            token_decimals = ether_scan.get_token_decimals(token_address)
                
            

            try:
                amount = amount / 10**token_decimals
            except Exception as e:
                print(e)
                amount = 'ERROR'                
            

            try:
                token_price = float(get_historical_token_price('ethereum', token_address, 'minute', date_end_timestamp)) # last monday to vote (deadline)
                amount_dollar = amount * token_price
            except Exception as e:
                print(e)
                try:
                    token_price = get_price_moralis('eth', token_address, block_number)['usdPrice']
                    amount_dollar = amount * token_price
                except Exception as e:
                    print(e)
                    token_price = 'ERROR'
                    amount_dollar = 'ERROR'
                
            print({'Date GMT': date, 'Round': round, 'Token name': token_name, 'Token address': token_address, 'Token amount': amount, 'Token price': token_price, 'Amount $': amount_dollar, 'Gauge': gauge, 'Briber': briber, 'Timestamp': timestamp, 'Block Number': block_number, 'Tx hash': tx_hash})
            yield date, round, token_name, token_address, amount, token_price, amount_dollar, gauge, briber, timestamp, block_number, tx_hash


def create_sheet(round_number):
    wb = Workbook()
    ws = wb.active
    ws.append(['Date', 'Round', 'Token Name', 'Token Address', 'Token Amount', 'Token Price', 'Amount $', 'Gauge', 'Briber', 'Timestamp', 'Block Number', 'Tx Hash'])
    

    for bribe in get_bribes(round_number-1):
        ws.append(bribe)
    wb.save(f'Votium_Bribe_Round{round_number}.xlsx')    



