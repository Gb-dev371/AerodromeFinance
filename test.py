import pandas as pd
from openpyxl import Workbook
from curve.curve import get_gauge_weight_history

file = 'curve/curve_gauge_data_2.xlsx'
df = pd.read_excel(file)
rows = df.shape[0]
# print(rows)
cols = df.shape[1]
round1_timestamp = 1631664000
# round1 = roundx - 604800*x-1

def create_spreadsheets_with_gauge_data(gauge_symbol, gauge_address):
    wb = Workbook()
    ws = wb.active
    ws.append(['Timestamp Start Votation', 'Round', 'Gauge Symbol', 'Gauge Address', 'Gauge Relative Weight', 'Votes Amount', 'Emissions per week', 'Dolar Value Emissions', 'CRV Price'])
    print(gauge_address)
    try:
        for gauge_data in get_gauge_weight_history(gauge_address):
            gauge_data.insert(2, gauge_symbol)
            print(gauge_data)
            ws.append(gauge_data)
            wb.save(f"curve/GaugesDataCurve/SYMBOL={gauge_symbol}ADDRESS={gauge_address}.xlsx")
            print('Successfull')
    except:
        print(f'It was not possible to get gauge data. Gauge symbol: {gauge_symbol} and Gauge Address: {gauge_address}')
        ws.append(['ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR'])
        # return

# create_spreadsheets_with_gauge_data('FRAX+PYUSD (0XA558...)', '0xdc6d319fac1498125e871ccedf7f1b9998eba3c5')


def iterate_over_gauges(start_gauge_index:int):
    for gauge_index in range(start_gauge_index, rows):
        gauge_address = df['Gauge Address'][gauge_index]
        gauge_symbol = df['Pool Name'][gauge_index]
        create_spreadsheets_with_gauge_data(gauge_symbol, gauge_address)
        print(gauge_address)
        print(gauge_index)
        

iterate_over_gauges(0)
# create_spreadsheets_with_gauge_data('FRAX+PYUSD (0xA558…)', '0xdc6d319fac1498125e871ccedf7f1b9998eba3c5')