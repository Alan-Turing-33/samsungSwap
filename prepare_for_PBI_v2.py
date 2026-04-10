#! /usr/bin/env python
import pandas as pd
import polars as pl
import numpy as np
import configparser
import os
import shutil 
from pathlib import Path


samsungConfig =  configparser.ConfigParser()
samsungConfig.read_file(open ('samsungConfig.ini'))
weekly_raw_data = samsungConfig ['dir']['rawData'] 
last_month_raw_data =  samsungConfig ['dir']['4week']
base_dir = samsungConfig ['dir']['base'] 

def collect_dates ():
	global weekly_raw_data
	global last_month_raw_data
	global base_dir
	change = False 
	samsungConfig =  configparser.ConfigParser()
	samsungConfig.read_file(open ('samsungConfig.ini'))
	weekly_raw_data = samsungConfig.get('dir','rawData') 
	last_month_raw_data =  samsungConfig.get ('dir','4week')
	base_dir = samsungConfig ['dir']['base'] 
	response = input ('current date : ' + weekly_raw_data + ' Overwrite (enter to accept)?')  
	if len (response) != 0  :
	   weekly_raw_data = base_dir + '/' + response + '/'
	   samsungConfig.set ('dir','rawData', weekly_raw_data)
	   change = True 
	   
	response = input ('last months date : ' + last_month_raw_data + ' Overwrite (enter to accept)?')  
	if len (response) != 0 :
		last_month_raw_data = base_dir + '/' + response + '/'
		samsungConfig.set ('dir','rawData', last_month_raw_data)
		change = True
       	   
	
	
	if change :
		samsungConfig.write (open ('samsungConfig.ini', 'w')) 	


def move_files () : 
	try :
		os.makedirs (weekly_raw_data)
	except :
		print (weekly_raw_data, ' already exists') 
	p = Path (r"C:\Users\fn101139\Downloads")
	
	report = list (p.glob ('upstate_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (1).csv' )
	
	report = list (p.glob ('south_east_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (2).csv' )
	
	report = list (p.glob ('Washington_baltimore*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (3).csv' )
	
	report = list (p.glob ('mountain_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (4).csv' )
	
	report = list (p.glob ('great_lakes_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (5).csv' )
	
	report = list (p.glob ('Tri_state_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (6).csv' )
	
	report = list (p.glob ('New_york_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (7).csv' )
	
	report = list (p.glob ('south_central_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'report (8).csv' )		
    
	report = list (p.glob ('eNB Releases via RAVS cloud_*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data ) 	
	
	report = list (p.glob ('gNB Releases via RAVS cloud_*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data ) 	
	
	report = list (p.glob ('gNB NR Cell Summary_*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data ) 	
	
	p2 = Path (weekly_raw_data) 
	report = list (p2.glob ('*.csv'))
	for f in report :
		print ('moving ', f) 
		shutil.copy2 (f, r'C:\Users\fn101139\OneDrive - Nokia\power BI dashboard\_current' )	
		
	
          		
     


all_cells = pl.DataFrame ({'nrCellId' :[], 'freqType' : [], 'marketId' : []}, schema={ "nrCellId": pl.Int64, "freqType": str, "marketId": pl.Int64})


print ('start conversion : ', pd.Timestamp.now ())

two_Power_14 = 2 ** 14

def read_process_region (ravs_filename) :

# CSV files to parse

# Columns of interest and indices
# C: Global eNodeB ID - 2
# I: Full Object Path - 8 --> get LNCEL and LNRELGNBCELL value
# K: Value - 10

  global cBand_global
  global fdd_global   
  global all_cells
  print ("processing : ",  ravs_filename)
  try : 
     raw = pl.read_csv(ravs_filename, skip_rows =5, columns = ['eNodeB Group', 'Global eNodeB ID', 'Full Object Path', 'Value'])
  except: 
     print ('cannot process file') 
     return 0
  clean = raw.filter  (( pl.col ('eNodeB Group') != 'Decommissioned ENB Group') &  ( pl.col ('eNodeB Group') != 'Decommissioned Group'))
  print ('removed  Decommissioned Group :',  raw.shape [1] - clean.shape [1] )

# NR Cell ID Assignment
# Within a PLMN or network, a cell is uniquely identified by a 36-bit NR Cell Identity (NCI). The NCI is composed of the 22-bit gNB ID supporting the cell, together with the 14-bit cell ID within the gNB.  The left most 22-bits of the NCI correspond to the gNB ID.  The relationship between NCI, gNB ID, and 14-bit Cell ID is given here:
# NCI = gNB ID * 16384 + 14-bit Cell ID
# The 14-bit cell ID range has a numeric range from 0 to 16383.   The 14-bit cell ID is composed of a 10-bit Sector ID and 4-bit Carrier ID.  Where the leftmost 10-bits of the 14-bit Cell ID are the sector ID. The assigned cell ID is a function of both the sector ID and the carrier ID.  Note: The leftmost bit of the sector ID is reserved for future use.
# The relationship between 14-bit Cell ID, Sector ID & Carrier ID is given here:
# 14-bit Cell ID = Sector ID * 16 + Carrier ID
  
# now parsing Full Object PAth "MRBTS-78011/LNBTS-78011/LNCEL-1/LNRELGNBCELL-0"  
  added_values = clean.with_columns ([ (pl.col ('Value') //  two_Power_14).alias ('nbrGnbId'),
                                       (pl.col ('Value') %  two_Power_14).alias ('nbrCellId'),
									   (pl.when ((pl.col ('Global eNodeB ID') // 1000) < 300).then 
									      ((pl.col ('Global eNodeB ID') // 1000)).otherwise
										  ((pl.col ('Global eNodeB ID') // 1000) -300)).alias ('marketId')])

  added_values = added_values.with_columns ([ 	(pl.col('nbrCellId') // 16).alias ('Sector Id'), 
                                                (pl.col('nbrCellId') % 16).alias ('Carrier Id'), 
												((pl.col('nbrGnbId') // 1000) % 10).alias ('gNB Type')])
  added_values = added_values.with_columns ([pl.when (pl.col ('Carrier Id') == 10 ).then ('cBand').otherwise(
                                              pl.when (pl.col ('gNB Type') == 0).then ('mmW'). otherwise('FDD')).alias ('freqType')])
  added_values = added_values.rename ( {"Value" : "nrCellId"} ) 
  
  VzMarketIdList =  added_values.select ('marketId').unique().to_series().to_list()
  print ('markets : ', VzMarketIdList)

# check the frequency total 
  local_cells = added_values.select(['nrCellId', 'freqType', 'marketId']).unique() 
 
  frequency_bands =  local_cells.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))
  print ('Cells found in ', ravs_filename)
  print (frequency_bands)
  duplicates = all_cells.join (local_cells, on='nrCellId', how = 'inner')
 
  print ('already found')
  print (duplicates.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count()))  

  all_cells = pl.concat ([all_cells, local_cells],  how = 'vertical').unique()
  
#  for mkt in VzMarketIdList  :
#      added_values.filter(pl.col ('marketId')  ==   mkt).write_csv (weekly_raw_data +  "pl_eNB_per_" + str (mkt) + ".csv")
      
def process_nation_wide (source): 

  p = Path (source)
  report_files = list (p.glob('report*.csv')) 
  print ('files found : ', report_files)       
 
  for f in report_files :
     read_process_region (f)       


def store_nationwide_cells(new_date, all_cells) : 
     
	# compare against Nokia Cells, no additional enforcement 
	p = Path (new_date)
	gnb_files = list (p.glob ('gNB NR Cell Summary*.csv'))
	ravs_nokia_gNB_cells = pl.read_csv( gnb_files [0], sep = ';', eol_char = '\r') 
	nokia_cells = ravs_nokia_gNB_cells.get_column ('NR Cell Identity').to_list()
	print ('total nokia 5G cells found: ', len(nokia_cells)) 
	aa = all_cells.get_column('nrCellId').to_pandas()
	check_nokia = aa.isin(nokia_cells)
	all_cells = all_cells.with_columns (pl.Series (check_nokia).alias ('isNokia'))
	all_unique_cells = all_cells.select (['freqType', 'nrCellId', 'isNokia']).unique()   	
 	
	frequency_bands = all_unique_cells.groupby (by = ['freqType', 'isNokia']).agg(pl.col( 'nrCellId').count().alias ('#cells'))
	print ('cells found per vendor and band:')
	print (frequency_bands.sort)

	rapper = all_cells.to_pandas()
	rapper.to_excel (weekly_raw_data +  'nationwide_cells.xlsx')

	cells_SS_only = all_cells.filter ((pl.col('freqType')  != 'mmW') & (~ pl.col('isNokia')))
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
		print ('calculated....')
		print ('cBand       ', frequency_bands.filter ((pl.col('freqType') == 'cBand') & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD samsung ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD Nokia   ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( pl.col('isNokia'))) [0,2])		
	else :
	   
		global_result.at [snapshot_date, 'Date'] = snapshot_date
		global_result.at [snapshot_date, 'cBand']  =       frequency_bands.filter ((pl.col('freqType') == 'cBand') & ( ~pl.col('isNokia'))) [0,2]
		global_result.at [snapshot_date, 'FDD Samsung'] =  frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( ~pl.col('isNokia'))) [0,2]
		global_result.at [snapshot_date, 'FDD Nokia']  =   frequency_bands.filter ((pl.col('freqType') == 'FDD')   & (  pl.col('isNokia'))) [0,2]
		global_result.at [snapshot_date, 'mmW Samsung'] =  frequency_bands.filter ((pl.col('freqType') == 'mmW')   & ( ~pl.col('isNokia'))) [0,2]                                           
		global_result.at [snapshot_date, 'mmW Nokia']  =   frequency_bands.filter ((pl.col('freqType') == 'mmW')   & (  pl.col('isNokia'))) [0,2]
		print ('adding....')
		print ('cBand       ', frequency_bands.filter ((pl.col('freqType') == 'cBand') & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD samsung ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD Nokia   ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( pl.col('isNokia'))) [0,2])
	
	global_result.to_excel(base_dir + 'nationwide_cells_history.xlsx', 
								   sheet_name= 'hist total cells', index= False )
	  
	print ('end conversion : ', pd.Timestamp.now ())
	print ('end write : ', pd.Timestamp.now ())

def four_week_delta (new_date, old_date): 
	p = Path (new_date)
	eNB_files = list (p.glob ( 'eNB Releases via RAVS cloud*.csv'))
	try : 
		print ('reading current eNB from:', eNB_files[0] )
	except: 
		print (' no matching files found at: ', new_date)
		return

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

	old_p = Path (old_date)

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
	print ('last Month gnb on Air: ', len (last_month_gNB))

	delta_eNB = pd.DataFrame (last_month_eNB - current_eNB) 
	delta_gNB = pd.DataFrame (last_month_gNB - current_gNB) 

	print ('delta enb ', delta_eNB.shape[0]  )
	print ('delta gnb ', delta_gNB.shape[0]  )

	previous_month_samsung_cells = pd.read_excel (last_month_raw_data + 'nationwide_cells_SS_cBand_FDD.xlsx', 
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








#main 

# collect_dates()
# move_files()

process_nation_wide(weekly_raw_data)

store_nationwide_cells (weekly_raw_data, all_cells) 

four_week_delta(weekly_raw_data, last_month_raw_data)