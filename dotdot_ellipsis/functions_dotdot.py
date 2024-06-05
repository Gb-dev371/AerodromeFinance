from dotdot_ellipsis.functions import get_start_and_end_blocks_in_the_week, get_input_decoded, calculate_start_and_end_timestamp_in_the_week, calculate_start_timestamp_epoch_dotdot, calculate_start_timestamp_epoch_dotdot
from web3 import Web3
from ScanApi.info import bsc_scan
from ScanApi.utils.functions import timestamp_to_date
import json

dotdot_voting_address = '0x5e4b853944f54C8Cb568b25d269Cd297B8cEE36d'
dotdot_voting_abi = bsc_scan.get_contract_abi(dotdot_voting_address)
dotdot_voting_contract = bsc_scan.get_contract(dotdot_voting_address, dotdot_voting_abi)

START_TIMESTAMP = dotdot_voting_contract.functions.startTime().call() # timestamp that the first week started 


def get_votes_in_dotdot_for_a_specific_pool(lp_token:str, week):
    start_timestamp, end_timestamp = calculate_start_and_end_timestamp_in_the_week(week)
    start_block, end_block = get_start_and_end_blocks_in_the_week(week)
    start_timestamp_epoch_dotdot = calculate_start_timestamp_epoch_dotdot(start_timestamp)

    start_epoch_dotdot_date = timestamp_to_date(start_timestamp_epoch_dotdot)
    end_epoch_dotdot_date = timestamp_to_date(end_timestamp)

    response = dotdot_voting_contract.functions.getCurrentVotes().call(block_identifier=end_block)

    total_votes = response[0]
    infos_pools = response[1]

    for tuple in infos_pools:
        if tuple[0] == lp_token:
            votes_pool_dotdot = tuple[1]

    share = votes_pool_dotdot / total_votes
    dict_info = [{'Week': week, 'Start Epoch Date GMT': start_epoch_dotdot_date, 'End Epoch Date GMT': end_epoch_dotdot_date, 'Total Votes': total_votes, 'Pool Votes': votes_pool_dotdot, 'Share': share}]

    return dict_info


def voters_list_dotdot(week:int, lp_token):
    start_timestamp_week, end_timestamp_week = calculate_start_and_end_timestamp_in_the_week(week)
    start_epoch_timestamp = calculate_start_timestamp_epoch_dotdot(start_timestamp_week)
    end_epoch_timestamp = end_timestamp_week # Wednesday 23:59:59 UTC

    start_epoch_block_number = bsc_scan.get_block_number_by_timestamp(start_epoch_timestamp, 'before')
    end_epoch_block_number = bsc_scan.get_block_number_by_timestamp(end_epoch_timestamp, 'before')

    date_timestamp_week = timestamp_to_date(start_timestamp_week)
    date_start_epoch = timestamp_to_date(start_epoch_timestamp)
    print(date_timestamp_week)
    print(date_start_epoch)

    for tx in bsc_scan.get_transactions(dotdot_voting_address, start_block=start_epoch_block_number, end_block=end_epoch_block_number):
        if tx['functionName'] == 'vote(address[] _tokenVote, uint256[] _weights)':
            info_input = get_input_decoded(tx['to'], tx['input'])[1]
            # print(lp)
            i = 0
            for lp_token in info_input['_tokens']:
                if lp_token == lp_token:
                # yield tx
                    voter = tx['from']
                    tx_hash = tx['hash']
                    votes_amount_user = info_input['_votes'][i]
                    dict_info = {'Voter Address': {voter}, 'Votes': {votes_amount_user}, 'Tx hash': {tx_hash}}
                    print(dict_info)
                i+=1


def get_votes_in_dotdot_for_all_pools_in_a_week(week:int):
    """This function aims to get the total votes in a specific week, 
    the amount of votes for all pools and the % that each pool had in relation to the total votes

    Args:
        week (int): the week votation in Ellipsis Finance

    Returns:
        dict: _description_
    """

    start_timestamp, end_timestamp = calculate_start_and_end_timestamp_in_the_week(week)
    start_block, end_block = get_start_and_end_blocks_in_the_week(week)
    start_timestamp_epoch_dotdot = calculate_start_timestamp_epoch_dotdot(start_timestamp)

    start_epoch_dotdot_date = timestamp_to_date(start_timestamp_epoch_dotdot)
    end_epoch_dotdot_date = timestamp_to_date(end_timestamp)

    response = dotdot_voting_contract.functions.getCurrentVotes().call(block_identifier=end_block)

    total_votes = response[0]
    infos_pools = response[1]
    
    pools_data = []

    for tuple in infos_pools:
        lp_token = tuple[0]
        votes_pool_ellipsis =  tuple[1]
        share = votes_pool_ellipsis / total_votes

        try:
            pool_name = bsc_scan.get_token_symbol(lp_token)
        except Exception as e:
            print(f'It was not possible to get pool name for lp token address: {lp_token}. Error: {e}')
            pool_name = 'ERROR'

        pools_data.append({'Pool Name': pool_name, 'LP Token Address': lp_token, 'Pool Votes': votes_pool_ellipsis, 'Share': share})

    dict_info = [{'Week': week, 'Start Epoch Date GMT': start_epoch_dotdot_date, 'End Epoch Date GMT': end_epoch_dotdot_date, 'Total Votes': total_votes, 'Pools Data': pools_data}]
    return dict_info


def save_all_votes_for_a_specific_pool_in_dotdot_in_a_json_file(file_path, lp_token, week_start, week_end=None):
    if week_end == None:
        week_end = week_start
        
    dict_info = []
    for week in range(week_start, week_end+1):
        for votes_info in get_votes_in_dotdot_for_a_specific_pool(lp_token, week):
            print(votes_info)
            dict_info.append(votes_info)
    
    with open(file_path, 'a') as file:
        json.dump(dict_info, file, indent=4)


def save_all_votes_for_all_pools_in_dotdot_in_a_json_file(file_path, week_start, week_end=None):
    if week_end == None:
        week_end = week_start
        
    dict_info = []
    for week in range(week_start, week_end+1):
        for votes_info in get_votes_in_dotdot_for_all_pools_in_a_week(week):
            print(type(votes_info))
            print(votes_info)
            dict_info.append(votes_info)
    
    with open(file_path, 'a') as file:
        json.dump(dict_info, file, indent=4)