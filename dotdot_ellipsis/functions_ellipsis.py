from web3 import Web3
import json
from ScanApi.utils.functions import timestamp_to_date, convert_date_to_timestamp
from dotdot_ellipsis.functions import get_start_and_end_blocks_in_the_week, calculate_start_and_end_timestamp_in_the_week
from ScanApi.info import bsc_scan, bsc
import pandas as pd
import json


incentive_voting_address = Web3.to_checksum_address("0x4695e50A38E33Ea09D1F623ba8A8dB24219bb06a")
incentive_voting_abi = bsc_scan.get_contract_abi(incentive_voting_address)
incentive_voting_contract = bsc.eth.contract(address=incentive_voting_address,abi=incentive_voting_abi)

event_vote = incentive_voting_contract.events.VotedForIncentives()

current_week = incentive_voting_contract.functions.getWeek().call()


''' VOTES '''
def get_votes_in_ellipsis_for_a_specific_pool(week:int, lp_token:str):
    """This function aims to get the total votes in a specific week, 
    the amount of votes for a specific pool and the % that the pool had in relation to the total votes

    Args:
        week (int): the week votation in Ellipsis Finance
        lp_token (str): The LP token address

    Returns:
        _type_: _description_
    """

    start_timestamp, end_timestamp = calculate_start_and_end_timestamp_in_the_week(week)

    start_epoch_ellipsis_date = timestamp_to_date(start_timestamp)
    end_epoch_ellipsis_date = timestamp_to_date(end_timestamp)
    
    response = incentive_voting_contract.functions.getVotes(week).call()

    total_votes = response[0]
    infos_pools = response[1]

    for tuple in infos_pools:
        if tuple[0] == lp_token:
            pool_votes =  tuple[1]

    share = pool_votes / total_votes

    dict_info = [{'Week': week, 'Start Epoch Date GMT': start_epoch_ellipsis_date, 'End Epoch Date GMT': end_epoch_ellipsis_date, 'Total Votes': total_votes, 'Pool Votes': pool_votes, 'Share': share}]

    return dict_info
        

def get_voters_ellipsis_for_a_specific_pool(week:int, lp_token:str=None):
    """This functions aims to get all the addresses that voted in Ellipsis Finance in a specific week. 
    If the LP token arg is different than None, the function will get only the addresses that voted for a specific pool.

    Args:
        week ([int]): [the week votation in Ellipsis Finance]
        lp_token ([str], optional): [The LP token address]. Defaults to None.
    """

    start_timestamp_week, end_timestamp_week = calculate_start_and_end_timestamp_in_the_week(week)
    start_block_number_week = bsc_scan.get_block_number_by_timestamp(start_timestamp_week, 'before')
    end_block_number_week = bsc_scan.get_block_number_by_timestamp(end_timestamp_week, 'before')

    date_start_week = timestamp_to_date(start_timestamp_week)
    date_end_week = timestamp_to_date(end_timestamp_week)
    print(date_start_week)
    print(date_end_week)

    topic0 = '0x60375167541f48b69e65fd2c8f9e4b91de8c12bb2efed58fff270004a5ea21b9' # event_signature of vote event

    for log in bsc_scan.get_logs(incentive_voting_address, topic0, start_block_number_week, end_block_number_week):
        transaction_hash = log['transactionHash']
        block_number = Web3.to_int(hexstr=log['blockNumber'])
        
        receipt = bsc_scan.rpc.eth.get_transaction_receipt(transaction_hash)
        decode = event_vote.process_receipt(receipt) # tuple of dicts

        '''
        each dict has: 'args': {'lpToken', 'token', 'week', 'caller', 'amount'}, 'event', 'logIndex', 'transaxtionIndex', 'transactionHash', 'address', 'blockHash'
        '''

        for info in decode:

            block_number = info['blockNumber']
            tx_hash = Web3.to_hex(info['transactionHash'])
            timestamp = bsc_scan.get_timestamp(transaction_hash)

            date = timestamp_to_date(timestamp)

            args = info['args']
            voter = args['voter']
            lp_tokens = args['tokens']
            votes_amount = args['votes']
            user_votes_used = int(args['userVotesUsed'])
            total_user_votes = int(args['totalUserVotes'])

            line = {'Date': date, 'Voter': voter, 'LP Token': lp_tokens, 'Votes Amount': votes_amount,'Hash': tx_hash, 'User Votes Used': user_votes_used, 'Total User Votes': total_user_votes,  'Timestamp': timestamp, 'Block Number': block_number}

            if lp_token:
                if lp_token in lp_tokens:
                    print(line)
                    print()
            else:
                print(line)
                print()


def get_votes_for_all_pools_in_a_week(week:int):
    """This function aims to get the total votes in a specific week, 
    the amount of votes for all pools and the % that each pool had in relation to the total votes

    Args:
        week (int): the week votation in Ellipsis Finance

    Returns:
        list: list of a dict containing week, start_epoch_date_gmt, end_epoch_date_gmt, total_votes, pools_data(pool_name, lp_token_address, pool_votes, share)
    """

    start_timestamp, end_timestamp = calculate_start_and_end_timestamp_in_the_week(week)
    start_block, end_block = get_start_and_end_blocks_in_the_week(week)

    start_epoch_ellipsis_date = timestamp_to_date(start_timestamp)
    end_epoch_ellipsis_date = timestamp_to_date(end_timestamp)

    response = incentive_voting_contract.functions.getVotes(week).call()

    total_votes = response[0]
    infos_pools = response[1]
    
    pools_data = []

    for tuple in infos_pools:
        lp_token = tuple[0]
        pool_votes_ellipsis =  tuple[1]
        share = pool_votes_ellipsis / total_votes

        try:
            pool_name = bsc_scan.get_token_symbol(lp_token)
        except Exception as e:
            print(f'It was not possible to get pool name for lp token address: {lp_token}. Error: {e}')
            pool_name = 'ERROR'

        pools_data.append({'Pool Name': pool_name, 'LP Token Address': lp_token, 'Pool Votes': pool_votes_ellipsis, 'Share': share})

    dict_info = [{'Week': week, 'Start Epoch Date GMT': start_epoch_ellipsis_date, 'End Epoch Date GMT': end_epoch_ellipsis_date, 'Total Votes': total_votes, 'Pools Data': pools_data}]
    return dict_info


def save_all_votes_for_a_specific_pool_in_ellipsis_in_a_json_file(file_path, lp_token, week_start, week_end=None):
    if week_end == None:
        week_end = week_start
        
    dict_info = []
    for week in range(week_start, week_end+1):
        for votes_info in get_votes_in_ellipsis_for_a_specific_pool(week, lp_token):
            print(votes_info)
            dict_info.append(votes_info)
    
    with open(file_path, 'a') as file:
        json.dump(dict_info, file, indent=4)


def save_all_votes_for_all_pools_in_ellipsis_in_a_json_file(file_path, week_start, week_end=None):
    if week_end == None:
        week_end = week_start
        
    dict_info = []
    for week in range(week_start, week_end+1):
        for votes_info in get_votes_for_all_pools_in_a_week(week):
            print(votes_info)
            dict_info.append(votes_info)
    
    with open(file_path, 'a') as file:
        json.dump(dict_info, file, indent=4)

