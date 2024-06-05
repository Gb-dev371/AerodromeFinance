from ScanApi.scan_api import ScanApi
from ScanApi.info import eth_infura, API_KEY_ETHER_SCAN
from ScanApi.utils.functions import timestamp_to_date
from web3 import Web3
from eth_abi import decode

ether_scan = ScanApi(rpc=eth_infura, chain='ETH', api_key=API_KEY_ETHER_SCAN)
votium_bribe_address = '0x63942E31E98f1833A234077f47880A66136a2D1e'
votium_bribe_abi = ether_scan.get_contract_abi(votium_bribe_address)
votium_bribe_contract = ether_scan.get_contract(contract_address=votium_bribe_address, abi=votium_bribe_abi)

START_TIMESTAMP_ROUND1 = 1630951200
EPOCH_DURATION = 86400 * 14 # 2 weeks
roundDuration = 86400 * 5; # 5 days
deadlineDuration = 60 * 60 * 6; # 6 hours

for log in ether_scan.get_logs(votium_bribe_address, '0x7c0c0ef7f1ccead819631ed9c10b0728e76274ee5572b53716ea96e7ec735ffa', 19959959, 19959960):

        transaction_hash = log['transactionHash']
        block_number = Web3.to_int(hexstr=log['blockNumber'])

        timestamp = ether_scan.get_timestamp(transaction_hash)
        date = timestamp_to_date(int(timestamp))

        binary_event_log = eth_infura.to_bytes(hexstr=log['data'])
        topics = log['topics']
        round = Web3.to_int(hexstr=topics[1])
        gauge_address = "0x" + topics[2][26:]
        briber = "0x" + topics[3][26:]
        print('------')
        print(binary_event_log)
        print()
        input_decoded = decode(['(uint256,address,uint256,uint256,address[],bool)'], binary_event_log)
        print(input_decoded)
        print('------')
        