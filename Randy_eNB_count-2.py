#! /usr/bin/env python


import pandas as pd

# CSV files to parse

randy_file = 'C:/Users/fn101139/Documents/SamsungSwap/shrinkage_history_no_irisview_2022-05-22.csv'

all_eNB = pd.read_csv(randy_file)


active_eNB = all_eNB.loc [(all_eNB['AS_UE_QUANTITY:DENOM_RRC_CONNECTED_UE'] > 0) | 
                          (all_eNB['AS_UE_STATE:SIGN_CONN_ESTAB_ATT_MT'] > 0) | 
                          (all_eNB['AS_UE_STATE:SIGN_CONN_ESTAB_ATT_MT' ] > 0), ['MARKET', 'ENODEB']]

result = active_eNB.groupby (by = 'MARKET') ['ENODEB'].nunique()

print (result)
result_Nokia = result [result ['active_count'] == 'Nokia']

active_eNB_Nokia= set (active_eNB.loc [(['active_count'] == 'Nokia'), 'Row Labels'])


result_Nokia.write_excel ('C:/Users/fn101139/Documents/SamsungSwap/RAndy_eNB_2022-05-03.xlsx')

