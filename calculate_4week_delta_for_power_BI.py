# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 11:55:56 2023

@author: fn101139
"""

import numpy as np
import pandas as pd 
import configparser
import os



samsung_Config =  configparser.ConfigParser()
samsung_Config.read ('samsungConfig.ini')
current_raw_data = samsung_Config ['dir']['rawData'] 
last_month_raw_data =  samsung_Config ['dir']['4week']

# current_eNB_source = pd.read_csv('C:/Users/fn101139/Downloads/netsumRept today.csv', 
#                                skiprows=4, sep = "," , on_bad_lines = 'warn', 
#                                 usecols= ['Global eNodeB ID', 'eNodeB Operational State'], dtype = {'Global eNodeB ID' : 'Int64'})


eNB_files = [x for x in os.listdir(current_raw_data) if 'eNB Releases via RAVS' in x]
print ('reading current eNB from:', current_raw_data + eNB_files[0] )
current_eNB_source = pd.read_csv(current_raw_data + eNB_files[0], sep = ';' , on_bad_lines = 'warn')

filtered_eNB = current_eNB_source.loc [(current_eNB_source ['Area'] != 'Maintenance Area') &
                                       (current_eNB_source ['Planned NE Type'] != 'fzmBTS') &  
                                       (current_eNB_source ['eNB Operational State'] == 'onAir')]


gNB_files = [x for x in os.listdir(current_raw_data) if 'gNB Releases via RAVS' in x]
print ('reading current gNB from:', current_raw_data + gNB_files[0] ) 
current_gNB_source = pd.read_csv(current_raw_data + gNB_files[0], 
                                     sep = ";" , on_bad_lines = 'warn', usecols= ['MRBTS ID', 'gNB Operational State'], dtype = {'MRBTS ID' : 'Int64'})

 
#current_eNB = set (current_eNB_source.loc [ current_eNB_source ['eNodeB Operational State'] == 'onAir',  'Global eNodeB ID'])
current_eNB = set (filtered_eNB ['MRBTS ID'])

current_gNB = set (current_gNB_source.loc [current_gNB_source ['gNB Operational State'] == 'onAir', 'MRBTS ID'])

print ('current enb on Air: ', len (current_eNB))
print ('current gnb on Air: ', len (current_gNB))

# previous_month_eNB_source = pd.read_csv('C:/Users/fn101139/Downloads/netsumRept last month.csv', 
#                                          skiprows=4, sep = "," , on_bad_lines = 'warn', 
#                                          usecols= ['Global eNodeB ID', 'eNodeB Operational State'], dtype = {'Global eNodeB ID' : 'Int64'})

# previous_month_eNB_source = pd.read_csv(last_month_raw_data + 'eNodeB-N Sector Radio Network Summary.csv', 
#                                 skiprows=4, sep = "\t" , on_bad_lines = 'warn', 
#                                  dtype = {'Global eNodeB ID' : 'Int64'})

eNB_files = [x for x in os.listdir(last_month_raw_data) if 'eNB Releases via RAVS' in x]
print ('reading previous eNB from:', last_month_raw_data + eNB_files[0] )

last_month_eNB_source = pd.read_csv(last_month_raw_data + eNB_files[0], sep = ';' , on_bad_lines = 'warn')

gNB_files = [x for x in os.listdir(last_month_raw_data) if 'gNB Releases via RAVS' in x]
print ('reading prevous month gNB from:', last_month_raw_data + gNB_files[0] )    
last_month_gNB_source = pd.read_csv(last_month_raw_data + gNB_files[0], 
                                        sep = ";" , on_bad_lines = 'warn', 
                                        usecols= ['MRBTS ID', 'gNB Operational State' ], dtype = {'MRBTS ID' : 'Int64'})

filtered_eNB = last_month_eNB_source.loc [(last_month_eNB_source ['Area'] != 'Maintenance Area') &  
                                              (last_month_eNB_source ['Planned NE Type'] != 'fzmBTS') &  
                                       (last_month_eNB_source ['eNB Operational State'] == 'onAir')]

last_month_eNB = set (filtered_eNB ['MRBTS ID'])



last_month_gNB = set (last_month_gNB_source.loc 
                      [ last_month_gNB_source ['gNB Operational State'] == 'onAir',  'MRBTS ID'])

print ('last Month enb on Air: ', len (last_month_eNB))
print ('last Month gnb on Air: ', len (last_month_gNB))


delta_eNB = pd.DataFrame (last_month_eNB - current_eNB) 


delta_gNB = pd.DataFrame (last_month_gNB - current_gNB) 

print ('delta enb ', delta_eNB.shape[0]  )
print ('delta gnb ', delta_gNB.shape[0]  )

previous_month_samsung_cells = pd.read_excel (last_month_raw_data + 'nationwide_cells_SS_cBand_cmW.xlsx', 
                                       sheet_name='Sheet1', 
                                       usecols= ['nrCellId','marketId', 'freqType' ],  )

old_cells = set (previous_month_samsung_cells ['nrCellId'])

current_samsung_cells = pd.read_excel (current_raw_data + 'nationwide_cells_SS_cBand_cmW.xlsx', 
                                       sheet_name='Sheet1', 
                                       usecols= ['nrCellId','marketId', 'freqType' ],  )
#%%
new_cells = set (current_samsung_cells ['nrCellId'])

delta_cells = new_cells - old_cells 

print ('old total # cells = ', len(old_cells))
print ('current total # cells = ', current_samsung_cells ['nrCellId'].nunique()) 

print ('delta cells size:', len (delta_cells))

current_samsung_cells ['new Cell'] =  np.isin ( current_samsung_cells ['nrCellId'],  list (delta_cells) ) 

print ('new cells in frame:', current_samsung_cells['new Cell'].sum())


added_samsung_cells = current_samsung_cells [ current_samsung_cells ['new Cell']]

print ('starting write to file')



with pd.ExcelWriter('C:/Users/fn101139/OneDrive - Nokia/power BI dashboard/_current/4week_delta.xlsx') as writer:
    added_samsung_cells.to_excel (writer, sheet_name = "delta Samsung cells")
    delta_eNB.to_excel (writer, sheet_name = "delta Nokia eNB")
    delta_gNB.to_excel (writer, sheet_name = "delta Nokia gNB")
    


 
# delta_eNB ['marketId'] = np.where ((delta ['Global eNodeB ID'] // 1000) < 300, (result['Global eNodeB ID'] // 1000), (result['Global eNodeB ID'] // 1000) - 300)

