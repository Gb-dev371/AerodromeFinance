import requests 
import os
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY_BASE_SCAN = os.getenv('API_KEY_BASE_SCAN')


def get_contract_abi(contract_address):
    url = f'https://api.basescan.org/api?module=contract&action=getabi&address={contract_address}&apikey={API_KEY_BASE_SCAN}'
    try:
        response = requests.get(url)
    except Exception as e:
        print('An error ocurred. API connection failed.')
        print(e)
    else:
        data = response.json()
        try:
            return data['result']
        except:
            return 'An error ocurred. It was not possible to get the contract abi.'
        

def get_block_number_by_timestamp(timestamp, closest):
    url = f'https://api.basescan.org/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest={closest}&apikey={API_KEY_BASE_SCAN}'
    response = requests.get(url)
    data = response.json()
    
    return int(data['result'])