#! /usr/bin/env python
import pandas as pd
import polars as pl
import numpy as np
import configparser
import os
from pathlib import Path


samsungConfig =  configparser.ConfigParser()
samsungConfig.read ('samsungConfig.ini')
weekly_raw_data = samsungConfig ['dir']['rawData'] 
last_month_raw_data =  samsungConfig ['dir']['4week']
base_dir = samsungConfig ['dir']['base'] 

print ('start conversion : ', pd.Timestamp.now ())
# CSV files to parse

# Columns of interest and indices
# C: Global eNodeB ID - 2
# I: Full Object Path - 8 --> get LNCEL and LNRELGNBCELL value
# K: Value - 10

two_Power_14 = 2 ** 14

def read_process_region (ravs_filename) :
  global cBand_global
  global cmW_global   
  global all_cells
  print ("processing : ",  ravs_filename)
  try : 
     raw = pl.read_csv(ravs_filename, skip_rows =5, columns = ['eNodeB Group', 'Global eNodeB ID', 'Full Object Path', 'Value'])
  except: 
     print ('cannot process file') 
     return 0
  clean = raw.filter  (( pl.col ('eNodeB Group') != 'Decommissioned ENB Group') &  ( pl.col ('eNodeB Group') != 'Decommissioned Group'))
  print ('removed  Decommissioned Group :',  raw.shape [1] - clean.shape [1] )
  
# now parsing Full Object PAth "MRBTS-78011/LNBTS-78011/LNCEL-1/LNRELGNBCELL-0"  
  added_values = clean.with_columns ([ (pl.col ('Value') //  two_Power_14).alias ('nbrGnbId'),
                                       (pl.col ('Value') %  two_Power_14).alias ('nbrCellId'),
									   (pl.when ((pl.col ('Global eNodeB ID') // 1000) < 300).then 
									      ((pl.col ('Global eNodeB ID') // 1000)).otherwise
										  ((pl.col ('Global eNodeB ID') // 1000) -300)).alias ('marketId')])


  added_values = added_values.with_columns ([pl.when (pl.col ('nbrCellId') % 16 == 10 ).then ('cBand').otherwise(
                                              pl.when (pl.col ('nbrGnbId') %  10000 < 9000).then ('mmW'). otherwise('cmW')).alias ('freqType')])
  added_values = added_values.rename ( {"Value" : "nrCellId"} ) 
  
  VzMarketIdList =  added_values.select ('marketId').unique().to_series().to_list()
  print ('markets : ', VzMarketIdList)

# check the frequency total 
  local_cells = added_values.select(['nrCellId', 'freqType']).unique() 
 
  frequency_bands =  local_cells.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))
  print ('Cells found in ', ravs_filename)
  print (frequency_bands)
  duplicates = all_cells.join (local_cells, on='nrCellId', how = 'inner')
 
  print ('already found')
  print (duplicates.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count()))  

  all_cells = pl.concat ([all_cells, local_cells],  how = 'vertical').unique()
  
  for mkt in VzMarketIdList  :
      added_values.filter(pl.col ('marketId')  ==   mkt).write_csv (weekly_raw_data +  "pl_eNB_per_" + str (mkt) + ".csv")
      
# report_files = []

p = Path (weekly_raw_data)

report_files = list (p.glob('report*.csv')) 
# for candidate in os.listdir(weekly_raw_data):
#     if (os.path.isfile(os.path.join(weekly_raw_data, candidate)) and 
#        (('report' in candidate) or ('LNRELGNBCELL_nbrCellId' in candidate))):
#          report_files.append(candidate)
         
print ('files found : ', report_files)       

all_cells = pl.DataFrame ({'nrCellId' :[], 'freqType' : []}, schema={ "nrCellId": pl.Int64, "freqType": str})

for f in report_files :
     read_process_region (f)       

all_frequency_bands = all_cells.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells')).sort (['freqType'])
print (all_frequency_bands)

# compare against Nokia Cells, no additional enforcement 
gnb_files = list (p.glob ('gNB NR Cell Summary*.csv'))

ravs_nokia_gNB_cells = pl.read_csv( gnb_files [0], sep = ';', eol_char = '\r') 
# ravs_nokia_gNB_cells = ravs_nokia_gNB_cells.filter ((pl.col('NR Cell Operational State' ) == 'enabled') ).select (['NR Cell Identity', 'Frequency Band Indicator NR'])

all_nokia = all_cells.join(ravs_nokia_gNB_cells, how = 'inner', left_on = 'nrCellId', right_on='NR Cell Identity')
all_samsung = all_cells.join(ravs_nokia_gNB_cells, how = 'anti', left_on = 'nrCellId', right_on='NR Cell Identity')
nokia_frequency_bands = all_nokia.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))
print ('Nokia  cells found :')
print (nokia_frequency_bands)

nokia_frequency_bands = nokia_frequency_bands.to_pandas ()
nokia_frequency_bands.set_index ('freqType', inplace = True)
all_frequency_bands = all_frequency_bands.to_pandas () 
all_frequency_bands.set_index ('freqType', inplace = True)
samsung_frequency_bands  = all_frequency_bands
samsung_frequency_bands ['#cells'] = all_frequency_bands ['#cells'] - nokia_frequency_bands ['#cells']

print ('Samsung cells found :')
print (samsung_frequency_bands)


rapper = all_cells.to_pandas()
rapper.to_excel (weekly_raw_data +  'nationwide_cells.xlsx')


cells_SS_only = all_samsung.filter (pl.col('freqType')  != 'mmW')
rapper = cells_SS_only.to_pandas()
rapper.to_excel (weekly_raw_data +  'nationwide_cells_SS_cBand_cmW.xlsx')


global_result = pd.read_excel (base_dir + 'nationwide_cells_history.xlsx', 
                               sheet_name= 'hist total cells', 
                               dtype = {'Date' : str})

global_result.index = global_result ['Date']
   
path_split = weekly_raw_data.split('/') 
mm, dd, yyyy = path_split [(len (path_split) - 2) ].split ('-')
snapshot_date = yyyy + '-' + mm + '-' + dd   
new_data = global_result ['Date'].str.contains (snapshot_date) 

if (new_data.any()) :
   print ('no update required in global result file nationwide_cells_history.xlsx')
else :
   
   global_result.at [snapshot_date, 'Date'] = snapshot_date
   global_result.at [snapshot_date, 'cBand']  = all_frequency_bands.at [ 'cBand', '#cells']
   global_result.at [snapshot_date, 'cmW Samsung'] =  samsung_frequency_bands.at [ 'cmW', '#cells']
   global_result.at [snapshot_date, 'cmW Nokia']  = nokia_frequency_bands.at [ 'cmW', '#cells']
   global_result.at [snapshot_date, 'mmW Samsung'] =  samsung_frequency_bands.at [ 'mmW', '#cells']                                           
   global_result.at [snapshot_date, 'mmW Nokia']  = nokia_frequency_bands.at ['mmW', '#cells']

global_result.to_excel(base_dir + 'nationwide_cells_history.xlsx', 
                               sheet_name= 'hist total cells', index= False )


  
print ('end conversion : ', pd.Timestamp.now ())
print ('end write : ', pd.Timestamp.now ())

eNB_files = list (p.glob ( 'eNB Releases via RAVS*.csv'))
print ('reading current eNB from:', eNB_files[0] )
current_eNB_source = pd.read_csv(eNB_files[0], sep = ';' , on_bad_lines = 'warn')

filtered_eNB = current_eNB_source.loc [(current_eNB_source ['Area'] != 'Maintenance Area') &
                                       (current_eNB_source ['Planned NE Type'] != 'fzmBTS') &  
                                       (current_eNB_source ['eNB Operational State'] == 'onAir')]


gNB_files = list (p.glob ( 'gNB NR Cell Summary*.csv'))
current_gNB_source = pd.read_csv(gNB_files [0], 
                                     sep = ";" , on_bad_lines = 'warn', usecols= ['MRBTS ID', 'gNB Operational State'], dtype = {'MRBTS ID' : 'Int64'})

 
#current_eNB = set (current_eNB_source.loc [ current_eNB_source ['eNodeB Operational State'] == 'onAir',  'Global eNodeB ID'])
current_eNB = set (filtered_eNB ['MRBTS ID'])

current_gNB = set (current_gNB_source.loc [current_gNB_source ['gNB Operational State'] == 'onAir', 'MRBTS ID'])

print ('current enb on Air: ', len (current_eNB))
print ('current gnb on Air: ', len (current_gNB))



old_p = Path (last_month_raw_data)

eNB_files = list (old_p.glob ('eNB Releases via RAVS cloud*.csv'))
print ('reading previous eNB from:',  eNB_files[0] )

last_month_eNB_source = pd.read_csv( eNB_files[0], sep = ';' , on_bad_lines = 'warn')

gNB_files = list (old_p.glob ('gNB NR Cell Summary*.csv'))
print ('reading previous gNB from:',  gNB_files[0] )
    
last_month_gNB_source = pd.read_csv( gNB_files [0], 
                                        sep = ";" , on_bad_lines = 'warn', 
                                        usecols= ['MRBTS ID', 'gNB Operational State' ], dtype = {'MRBTS ID' : 'Int64'})

filtered_eNB = last_month_eNB_source.loc [(last_month_eNB_source ['Area'] != 'Maintenance Area') &  
                                              (last_month_eNB_source ['Planned NE Type'] != 'fzmBTS') &  
                                       (last_month_eNB_source ['eNB Operational State'] == 'onAir')]

last_month_eNB = set (filtered_eNB ['MRBTS ID'])



last_month_gNB = set (last_month_gNB_source.loc 
                      [ last_month_gNB_source ['gNB Operational State'] == 'onAir',  'MRBTS ID'])

print ('last Month enb on Air: ', len (last_month_eNB))
print ('lasrt Month gnb on Air: ', len (last_month_gNB))


delta_eNB = pd.DataFrame (last_month_eNB - current_eNB) 

delta_gNB = pd.DataFrame (last_month_gNB - current_gNB) 

print ('delta enb ', delta_eNB.shape[0]  )
print ('delta gnb ', delta_gNB.shape[0]  )

previous_month_samsung_cells = pd.read_excel (last_month_raw_data + 'nationwide_cells_SS_cBand_cmW.xlsx', 
                                       sheet_name='Sheet1')

old_cells = set (previous_month_samsung_cells ['nrCellId'])

current_samsung_cells = pd.read_excel (weekly_raw_data + 'nationwide_cells_SS_cBand_cmW.xlsx', 
                                       sheet_name='Sheet1')
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






