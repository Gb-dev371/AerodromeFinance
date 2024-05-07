from moralis import evm_api
import os
from dotenv import load_dotenv

def get_price_moralis(chain, token_address, block_number):
  api_key = os.getenv('MORALIS_API_KEY')

  params = {
    "chain": chain,
    "include": "percent_change",
    "address": token_address,
    'to_block': block_number
  }

  result = evm_api.token.get_token_price(
    api_key=api_key,
    params=params,
  )

  return result