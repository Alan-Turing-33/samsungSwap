#! /usr/bin/env python


import pandas as pd

# CSV files to parse

randy_file = 'C:/Users/fn101139/Documents/SamsungSwap/SNAP_Summary_2022-05-03.xlsx'

active_eNB = pd.read_excel(randy_file)

lastColIndex = active_eNB.shape[1] - 1 

lastCol = active_eNB.columns[lastColIndex]

active_eNB.rename (columns = {lastCol : 'active_count'}, inplace= True)

result = active_eNB.groupby (by = ['Market', 'active_count']).count()
result.reset_index(inplace =True)

result_Nokia = result [result ['active_count'] == 'Nokia']

active_eNB_Nokia= set (active_eNB.loc [(['active_count'] == 'Nokia'), 'Row Labels'])


result_Nokia.write_excel ('C:/Users/fn101139/Documents/SamsungSwap/RAndy_eNB_2022-05-03.xlsx')

