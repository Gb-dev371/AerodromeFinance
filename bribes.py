from ScanApi.scan_api import ScanApi
from ScanApi.utils.functions import timestamp_to_date, convert_date_to_timestamp
from web3 import Web3


def get_pool_name(scan_api:ScanApi, pool_contract_address):
    pool_abi = scan_api.get_contract_abi(pool_contract_address)
    pool_contract = scan_api.get_contract(pool_contract_address, pool_abi)
    return pool_contract.functions.name().call()
    

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
                
                name = get_pool_name(scan_api, pool_contract_address)
                tx_hash = tx['hash']
                timestamp = scan_api.get_timestamp(tx_hash)
                date = timestamp_to_date(timestamp)
                input_decoded['Tx hash'] = tx_hash
                input_decoded['Timestamp'] = timestamp
                input_decoded['Block Number'] = block_number
                input_decoded['Date'] = date
                input_decoded['Name'] = name
                bribe_pool_list.append(input_decoded)
            
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

