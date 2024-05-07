from dotenv import load_dotenv
from web3 import Web3
import os

load_dotenv(override=True)
API_KEY_BINANCE_SCAN = os.getenv('BINANCE_SCAN_API_KEY')
API_KEY_POLYGON_SCAN = os.getenv('POLYGON_SCAN_API_KEY')
API_KEY_INFURA = os.getenv('INFURA_API_KEY')
NODE_URL = os.getenv('NODE_URL')
API_KEY_BASE_SCAN = os.getenv('API_KEY_BASE_SCAN')

pol = Web3(Web3.HTTPProvider(f'https://polygon-mainnet.infura.io/v3/{API_KEY_INFURA}'))
base = Web3(Web3.HTTPProvider(NODE_URL))
