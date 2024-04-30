import requests
import os
from dotenv import load_dotenv
from web3 import Web3
from utils import get_block_number_by_timestamp, get_contract_abi

load_dotenv(override=True)
NODE_URL = os.getenv('NODE_URL')
API_KEY_BASE_SCAN = os.getenv('API_KEY_BASE_SCAN')
base_node = Web3(Web3.HTTPProvider(NODE_URL))
        

voter_aerodrome_address = Web3.to_checksum_address('0x16613524e02ad97eDfeF371bC883F2F5d6C480A5')
voter_aerodrome_abi = get_contract_abi('0x16613524e02ad97eDfeF371bC883F2F5d6C480A5')
voter_aerodrome_contract = base_node.eth.contract(address=voter_aerodrome_address, abi=voter_aerodrome_abi)


''' VOTES '''
def get_pool_votes_in_a_timestamp(pool, timestamp):
    """_summary_

    Args:
        pool (str): _description_
        timestamp (int): _description_

    Returns:
        dict: A dict with data about votes that the pool received
    """

    pool_address = Web3.to_checksum_address(pool)

    end_timestamp_votation  = voter_aerodrome_contract.functions.epochVoteEnd(timestamp).call()

    end_block_week = get_block_number_by_timestamp(end_timestamp_votation, 'before')

    try:
        pool_votes = voter_aerodrome_contract.functions.weights(pool_address).call(block_identifier=end_block_week) / 10**18 # pode dar erro caso coloque uma semana em que essa pool não podia receber votação
    except:
        pool_votes = 'ERROR'

    try:
        total_votes = voter_aerodrome_contract.functions.totalWeight().call(block_identifier=end_block_week) / 10**18
    except:
        total_votes = 'ERROR'

    share = pool_votes / total_votes
        
    return {'Pool Address': pool, 'Pool Votes': pool_votes, 'Share': share, 'Total Votes': total_votes, 'Timestamp': timestamp}


def get_all_votes_for_all_pools_in_the_week(timestamp):
    """_summary_

    Args:
        timestamp (int): timestamp choosed by user

    Yields:
        dict: A dict with data about votes that the pool received
    """

    block_number = get_block_number_by_timestamp(timestamp, 'before')

    length = voter_aerodrome_contract.functions.length().call(block_identifier=block_number)

    for i in range(0, length):
        pool_address = voter_aerodrome_contract.functions.pools(i).call(block_identifier=block_number)
        pool_votes_info = get_pool_votes_in_a_timestamp(pool_address, timestamp)
        yield pool_votes_info


