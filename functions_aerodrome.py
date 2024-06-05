import requests
import os
from dotenv import load_dotenv
from web3 import Web3
from ScanApi.scan_api import ScanApi
from ScanApi.utils.functions import timestamp_to_date, convert_date_to_timestamp
from get_price_moralis import get_price_moralis

load_dotenv(override=True)
NODE_URL = os.getenv('NODE_URL')
API_KEY_BASE_SCAN = os.getenv('API_KEY_BASE_SCAN')
base_node = Web3(Web3.HTTPProvider(NODE_URL))


def get_pool_name(scan_api:ScanApi, pool_contract_address):
    pool_abi = scan_api.get_contract_abi(pool_contract_address)
    pool_contract = scan_api.get_contract(pool_contract_address, pool_abi)
    return pool_contract.functions.name().call()


''' VOTES '''
def get_pool_votes_in_a_timestamp(scan_api:ScanApi, pool, voter_contract, timestamp):
    """_summary_

    Args:
        pool (str): Pool address
        voter_contract: Instancy of the contract
        timestamp (int): timestamp to get the pool votes

    Returns:
        dict: A dict with data about votes that the pool received
    """

    pool_address = Web3.to_checksum_address(pool)

    end_timestamp_votation  = voter_contract.functions.epochVoteEnd(timestamp).call()

    end_block_week = scan_api.get_block_number_by_timestamp(end_timestamp_votation, 'before')

    try:
        pool_votes = voter_contract.functions.weights(pool_address).call(block_identifier=end_block_week) / 10**18 # pode dar erro caso coloque uma semana em que essa pool não podia receber votação
    except:
        pool_votes = 'ERROR'

    try:
        total_votes = voter_contract.functions.totalWeight().call(block_identifier=end_block_week) / 10**18
    except:
        total_votes = 'ERROR'

    share = pool_votes / total_votes
        
    return {'Pool Address': pool, 'Pool Votes': pool_votes, 'Share': share, 'Total Votes': total_votes, 'Timestamp': timestamp}


def get_all_votes_for_all_pools_in_the_week(scan_api:ScanApi, voter_contract, timestamp):
    """_summary_

    Args:
        timestamp (int): timestamp choosed by user

    Yields:
        dict: A dict with data about votes that the pool received
    """

    block_number = scan_api.get_block_number_by_timestamp(timestamp, 'before')

    length = voter_contract.functions.length().call(block_identifier=block_number)

    for i in range(0, length):
        pool_address = voter_contract.functions.pools(i).call(block_identifier=block_number)
        pool_votes_info = get_pool_votes_in_a_timestamp(pool_address, timestamp)
        yield pool_votes_info


    
''' BRIBES '''
def get_bribes_created(scan_api:ScanApi, pool_contract_address, voter_contract_address='0x16613524e02ad97eDfeF371bC883F2F5d6C480A5', start_block=0, end_block=99999999):
    pool_contract_address = Web3.to_checksum_address(pool_contract_address)
    bribe_pool_list = []
    voter_contract_abi = scan_api.get_contract_abi(voter_contract_address)
    voter_contract = scan_api.get_contract(voter_contract_address, voter_contract_abi)

    gauge_address = voter_contract.functions.gauges(pool_contract_address).call()
    bribe_contract_address = voter_contract.functions.gaugeToBribe(gauge_address).call()

    for tx in scan_api.get_transactions(bribe_contract_address, start_block=start_block, end_block=end_block):
        
        if (tx['to']).lower() == bribe_contract_address.lower():
            
            if tx['functionName'] == 'notifyRewardAmount(address _rewardsToken, uint256 reward)':
                
                block_number = int(tx['blockNumber'])
                input_data = tx['input']
                input_decoded = scan_api.get_input_decoded(bribe_contract_address, input_data)[1] # {'token': '0xA3d1a8DEB97B111454B294E2324EfAD13a9d8396', 'amount': 250000000000000000000}
                token_address = input_decoded['token']
                token_amount = input_decoded['amount']
                
                pool_name = get_pool_name(scan_api, pool_contract_address)
                tx_hash = tx['hash']
                timestamp = scan_api.get_timestamp(tx_hash)
                date = timestamp_to_date(timestamp)
                
                token_abi = scan_api.get_contract_abi(token_address)

                try:
                    token_decimals = int(scan_api.get_token_decimals(token_address, token_abi))
                    token_amount /= 10 ** token_decimals
                    token_symbol = scan_api.get_token_symbol(token_address, token_abi)
                except:
                        token_symbol = 'ERROR'
                try:
                    price_token = get_price_moralis('base', token_address, block_number)['usdPrice']
                except Exception as e:
                    price_token = 'ERROR'

                
                line = {'Token address': token_address, 'Token symbol': token_symbol, 'Token amount': token_amount, 'Amount in $': '', 'Token value': price_token, 'Pool name': pool_name, 'Pool address': pool_contract_address, 'Tx hash': tx_hash, 'Timestamp': timestamp, 'Block number': block_number, 'Date': date}
                bribe_pool_list.append(line)
            
    return bribe_pool_list


def get_all_bribes_for_all_pools(scan_api:ScanApi, start_date, end_date, voter_contract_address='0x16613524e02ad97eDfeF371bC883F2F5d6C480A5'):
    start_timestamp = convert_date_to_timestamp(start_date)
    end_timestamp = convert_date_to_timestamp(end_date)

    start_block = scan_api.get_block_number_by_timestamp(start_timestamp, 'before')
    end_block = scan_api.get_block_number_by_timestamp(end_timestamp, 'before')

    voter_contract_abi = scan_api.get_contract_abi(voter_contract_address)
    voter_contract = scan_api.get_contract(voter_contract_address, voter_contract_abi)
    length = voter_contract.functions.length().call()
    for i in range(0, length):
        pool_address = voter_contract.functions.pools(i).call()
        bribe_pool_list = get_bribes_created(scan_api, pool_address, voter_contract_address, start_block=start_block, end_block=end_block)
        yield bribe_pool_list

    
