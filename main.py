from functions_aerodrome import get_all_votes_for_all_pools_in_the_week, get_pool_votes_in_a_timestamp
from bribes import get_all_bribes_for_all_pools
from ScanApi.scan_api import ScanApi
from info import base, API_KEY_BASE_SCAN
from web3 import Web3

# print(get_pool_votes_in_a_timestamp('pool address', timestamp=''))

base_scan = ScanApi(rpc=base, chain='BASE', api_key=API_KEY_BASE_SCAN)

voter_aerodrome_address = Web3.to_checksum_address('0x16613524e02ad97eDfeF371bC883F2F5d6C480A5')
voter_aerodrome_abi = base_scan.get_contract_abi('0x16613524e02ad97eDfeF371bC883F2F5d6C480A5')
voter_aerodrome_contract = base_scan.rpc.eth.contract(address=voter_aerodrome_address, abi=voter_aerodrome_abi)


for bribe in get_all_bribes_for_all_pools(base_scan, '2024-05-01 10:00:00', '2024-05-07 10:00:00', voter_contract_address='0x16613524e02ad97eDfeF371bC883F2F5d6C480A5'):
    print(bribe)