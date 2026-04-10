#! /usr/bin/env python


import pandas as pd
import numpy as np
import configparser

samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')

weekly_raw_data = samsungConfig ['dir']['rawData'] 

# CSV files to parse

resultFileName = weekly_raw_data + 'sectorResult_permarket.xlsx'
cmWaveAuditFile = weekly_raw_data + 'gnb_4_cmWave.csv'
mmWaveAuditFile = weekly_raw_data + 'gnb_4_mmWave.csv'


readAudit = pd.read_csv(mmWaveAuditFile)
all_Nokia_mmW =  set (readAudit ['gNB_number'])

readAudit = pd.read_csv(cmWaveAuditFile)
all_Nokia_cmW = set (readAudit ['gNB_number'])

ravs_gNB = pd.read_csv( 'C:/Users/fn101139/Downloads/gNB NR Cell Summary_20221209_20221209000917.csv', sep = ';', on_bad_lines = 'warn')
#%%
ravs_cmWave = set (ravs_gNB.loc [ (ravs_gNB['gNB Operational State' ] == 'onAir') & 
                                 ((ravs_gNB['Planned NE Type' ] == '5gClassicalBTS') | 
                                  (ravs_gNB['Planned NE Type' ] == 'sBTS')), 'MRBTS ID' ])
ravs_cmWave = set (ravs_gNB.loc [ (ravs_gNB['Planned NE Type' ] == '5gClassicalBTS') | 
                                  (ravs_gNB['Planned NE Type' ] == 'sBTS'), 'MRBTS ID' ])

print (len (ravs_cmWave))
ravs_mmWave = set (ravs_gNB.loc [ (ravs_gNB['gNB Operational State' ] == 'enabled') & 
                                  (ravs_gNB['Planned NE Type' ] == '5gCU') , 'MRBTS ID' ])
print (len (ravs_mmWave))





print ( 'delta cm in RAVS, not in Ravi : ',  len (ravs_cmWave - all_Nokia_cmW) ) 
print ( 'delta cm in Ravi , not in RAVS: ',  len (all_Nokia_cmW - ravs_cmWave ) ) 


print ( 'delta mm in RAVS, not in Ravi : ',  len (ravs_mmWave - all_Nokia_mmW) ) 
print ( 'delta mm in Ravi , not in RAVS: ',  len (all_Nokia_mmW - ravs_mmWave)  ) 

