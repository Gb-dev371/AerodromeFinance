from ScanApi.info import bsc_scan
from web3 import Web3
from datetime import datetime

DddIncentiveDistributor = Web3.to_checksum_address('0x4625928fCb2Ece1Aca3dd2B992f7e2e4d9596446')
DddIncentiveDistributor_abi = bsc_scan.get_contract_abi(DddIncentiveDistributor)
ddd_incentive_distributor_contract = bsc_scan.rpc.eth.contract(address=DddIncentiveDistributor, abi=DddIncentiveDistributor_abi)
event_bribe = ddd_incentive_distributor_contract.events.IncentiveReceived()

dotdot_voting_address = '0x5e4b853944f54C8Cb568b25d269Cd297B8cEE36d'
dotdot_voting_abi = bsc_scan.get_contract_abi(dotdot_voting_address)
dotdot_voting_contract = bsc_scan.get_contract(dotdot_voting_address, dotdot_voting_abi)
timestamp_atual = int(datetime.now().timestamp())

START_TIMESTAMP = dotdot_voting_contract.functions.startTime().call() # timestamp that the first week started 


def calculate_start_and_end_timestamp_in_the_week(week:int):
    start_timestamp_week = START_TIMESTAMP + 604800*week
    end_timestamp_week = start_timestamp_week + 604799

    if end_timestamp_week > timestamp_atual:
        end_timestamp_week = timestamp_atual
    

    return start_timestamp_week, end_timestamp_week


def get_start_and_end_blocks_in_the_week(week:int):
    start_timestamp_week, end_timestamp_week = calculate_start_and_end_timestamp_in_the_week(week)
    
    start_block_week = bsc_scan.get_block_number_by_timestamp(start_timestamp_week, 'before')
    
    try:
        end_block_week = bsc_scan.get_block_number_by_timestamp(end_timestamp_week, 'before')
    except:
        end_block_week = bsc_scan.rpc.eth.get_block_number()

    return start_block_week, end_block_week


def calculate_start_timestamp_epoch_dotdot(start_timestamp_week:int):
    '''
    Params: Timestamp of the beggining of the week (always Thursday 00:00:00 UTC)
    Returns the timestamp of the beggining of DotDot voting epoch (always Monday 00:00:00 UTC)
    '''
    return start_timestamp_week + 86400*4


def get_input_decoded(contract_address, input_data):
    contract_address = Web3.to_checksum_address(contract_address)
    abi = bsc_scan.get_contract_abi(contract_address)
    contract = bsc_scan.get_contract(address=contract_address, abi=abi)
    return contract.decode_function_input(input_data)
