#! /usr/bin/env python
import pandas as pd
import polars as pl
import numpy as np
import configparser
import os

samsungConfig =  configparser.ConfigParser()
samsungConfig.read ('samsungConfig.ini')
weekly_raw_data = samsungConfig ['dir']['rawData'] 
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
      
report_files = []

for candidate in os.listdir(weekly_raw_data):
    if (os.path.isfile(os.path.join(weekly_raw_data, candidate)) and 
        (('report' in candidate) or ('LNRELGNBCELL_nbrCellId' in candidate))):
         report_files.append(candidate)
         
print ('files found : ', report_files)       

all_cells = pl.DataFrame ({'nrCellId' :[], 'freqType' : []}, schema={ "nrCellId": pl.Int64, "freqType": str})

for f in report_files :
     read_process_region (weekly_raw_data + f)       

all_frequency_bands = all_cells.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))
print (all_frequency_bands)

# compare against Nokia Cells, no additional enforcement 
ravs_nokia_gNB_cells = pl.read_csv( weekly_raw_data  + 'gNB NR Cell Summary.csv', sep = ';', eol_char = '\r') 
# ravs_nokia_gNB_cells = ravs_nokia_gNB_cells.filter ((pl.col('NR Cell Operational State' ) == 'enabled') ).select (['NR Cell Identity', 'Frequency Band Indicator NR'])

all_nokia = all_cells.join(ravs_nokia_gNB_cells, how = 'inner', left_on = 'nrCellId', right_on='NR Cell Identity')
nokia_frequency_bands = all_nokia.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))
print ('Nokia  cells found :')
print (nokia_frequency_bands)

samsung_frequency_bands = all_frequency_bands.select('#cells') - nokia_frequency_bands.select ('#cells') 

#  all_nokia.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))


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
   global_result.at [snapshot_date, 'cBand']  = all_frequency_bands.filter(pl.col('freqType') == 'cBand').select ('#cells')
   global_result.at [snapshot_date, 'cmW Samsung'] =  samsung_frequency_bands.filter(pl.col('freqType') == 'cmW').select ('#cells')
   global_result.at [snapshot_date, 'cmW Nokia']  = nokia_frequency_bands.filter(pl.col('freqType') == 'cmW').select ('#cells')
   global_result.at [snapshot_date, 'mmW Samsung'] =  samsung_frequency_bands.filter(pl.col('freqType') == 'mmW').select ('#cells')                                                
   global_result.at [snapshot_date, 'mmW Nokia']  = nokia_frequency_bands.filter(pl.col('freqType') == 'mmW').select ('#cells')  

global_result.to_excel(base_dir + 'nationwide_cells_history.xlsx', 
                               sheet_name= 'hist total cells', index= False )


  
print ('end conversion : ', pd.Timestamp.now ())
print ('end write : ', pd.Timestamp.now ())
