import pandas as pd
from functions_aerodrome import get_all_bribes_for_all_pools

def new_line(token_address, amount, tx_hash, timestamp, block_number, date, pool_name):
    return {'Token': token_address, 'Amount': amount, 'Tx hash': tx_hash, 'Timestamp': timestamp, 'Block Number': block_number, 'Date': date, 'Name': pool_name}


def write_sheet_bribes(scan_api, start_date, end_date, voter_contract_address):
    arquivo = 'bribes.xlsx'

    df = pd.read_excel(arquivo)
    for bribe_pool_list in get_all_bribes_for_all_pools(scan_api, start_date, end_date, voter_contract_address):
        if len(bribe_pool_list) > 0:
            # print(bribe_pool_list)
            line = bribe_pool_list[0]
            df = df._append(line, ignore_index=True)
    df.to_excel(arquivo, index=False)
