#! /usr/bin/env python
import pandas as pd
import polars as pl
import numpy as np
import configparser
import os
import shutil 
from pathlib import Path
import datetime
import polars.selectors as cs

new_work_dir, discard  = os.path.split( os.path.abspath(__file__))
print ('new working dir : ', new_work_dir)

samsungConfig =  configparser.ConfigParser()
samsungConfig.read_file(open ( new_work_dir + '\\'+ 'samsungConfig.ini'))
     
base_dir = samsungConfig ['dir']['base'] 

def last_sunday () : 
	current_day = datetime.date.today()
	count_day_back_to_Sunday =   datetime.timedelta (days = current_day.weekday() + 1)
	sunday_date = current_day - count_day_back_to_Sunday
	print (sunday_date)
	return sunday_date.isoformat() 

def four_weeks_back (current_date):
   sample_date =  datetime.date.fromisoformat (current_date)
   four_weeks = datetime.timedelta (days = 28)
   fourweekback_date = sample_date - four_weeks 
   return  fourweekback_date.isoformat()

def collect_dates (samsungConfig):
	base_dir = samsungConfig ['dir']['base']
	weekly_raw_data = samsungConfig.get('dir','rawData') 
	raw_date = weekly_raw_data.split ('/') [-2]
	suggested_date = last_sunday() 	
	new_current_date = input ('current date : ' + suggested_date + ' Overwrite (enter to accept)?')  
	if (len (new_current_date) != 0)  : 
		weekly_raw_data = base_dir  + new_current_date + '/'
		raw_date = new_current_date
	elif (raw_date != suggested_date) : 
		weekly_raw_data = base_dir  + suggested_date + '/'
		raw_date = suggested_date   	
	four_weeks_back_date = four_weeks_back(raw_date)
	four_weeks_back_raw_data = base_dir + four_weeks_back_date + '/'
	return  weekly_raw_data, four_weeks_back_raw_data

def delete_files (target_dir) :
	p = Path (target_dir)
	report = list (p.glob ('?NB Releases via RAVS cloud_*.csv'))
	print ('found matching files: {}'.format( report))
	for f in report:
		print ('remove  {}'.format (f)) 
		os.remove (f)
	
	report = list (p.glob ('gNB NR Cell Summary_*.csv')) 
	print ('found matching files: {}'.format( report))

	for f in report:
		print ('remove  {}'.format (f)) 
		os.remove (f)	
	
	print ('{} target_dir'.format (r'\allNetwork_x2linkStat.csv')) 
	os.remove (target_dir + r'\allNetwork_x2linkStat.csv')




def move_files () : 
	try :
		os.makedirs (weekly_raw_data)
	except :
		print (weekly_raw_data, ' already exists') 
	p = Path (r"C:\Users\fn101139\Downloads")
	
	report = list (p.glob ('upstate_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	print ('moving ', latest_version)
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
	
	report = list (p.glob ('allNetwork_x2linkStat*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, weekly_raw_data + r'allNetwork_x2linkStat.csv' )  	
	
	
	
	p2 = Path (weekly_raw_data) 
	report = list (p2.glob ('*.csv'))
	for f in report :
		print ('moving ', f) 
		shutil.copy2 (f, r'C:\Users\fn101139\OneDrive - Nokia\power BI dashboard\_current' )	
		
	
          		
     


all_cells = pl.DataFrame ({'nrCellId' :[], 'nbrGnbId':[], 'nbrCellId':[], 'Sector Id':[], 'Carrier Id':[], 'gNB Type':[], 'freqType' :[]}, 
schema={ "nrCellId": pl.Int64,  'nbrGnbId' : pl.Int64, 'nbrCellId' : pl.Int64, 'Sector Id' : pl.Int64, 'Carrier Id' : pl.Int64, 'gNB Type' : pl.Int64, "freqType": str })


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
  clean = clean.cast ({'Value' : pl.Int64})
  if (clean.shape [0] == 0):
   print ('no data found' ) 
   return 
  else : 
    clean = clean.cast ({'Value' : pl.Int64})
# NR Cell ID Assignment
# Within a PLMN or network, a cell is uniquely identified by a 36-bit NR Cell Identity (NCI). The NCI is composed of the 22-bit gNB ID supporting the cell, together with the 14-bit cell ID within the gNB.  The left most 22-bits of the NCI correspond to the gNB ID.  The relationship between NCI, gNB ID, and 14-bit Cell ID is given here:
# NCI = gNB ID * 16384 + 14-bit Cell ID
# The 14-bit cell ID range has a numeric range from 0 to 16383.   The 14-bit cell ID is composed of a 10-bit Sector ID and 4-bit Carrier ID.  Where the leftmost 10-bits of the 14-bit Cell ID are the sector ID. The assigned cell ID is a function of both the sector ID and the carrier ID.  Note: The leftmost bit of the sector ID is reserved for future use.
# The relationship between 14-bit Cell ID, Sector ID & Carrier ID is given here:
# 14-bit Cell ID = Sector ID * 16 + Carrier ID
  
# now parsing Full Object PAth "MRBTS-78011/LNBTS-78011/LNCEL-1/LNRELGNBCELL-0"  

  
  added_values = clean.with_columns ([ (pl.col ('Value') //  2**14).alias ('nbrGnbId'),
                                       (pl.col ('Value') %  2**14).alias ('nbrCellId'),
									   (pl.when ((pl.col ('Global eNodeB ID') // 1000) < 300).then 
									      ((pl.col ('Global eNodeB ID') // 1000)).otherwise
										  ((pl.col ('Global eNodeB ID') // 1000) -300)).alias ('marketId')])

  added_values = added_values.with_columns ([ 	(pl.col('nbrCellId') // 16).alias ('Sector Id'), 
                                                (pl.col('nbrCellId') % 16).alias ('Carrier Id'), 
												((pl.col('nbrGnbId') // 1000) % 10).alias ('gNB Type')])
  added_values = added_values.with_columns ([pl.when (pl.col ('Carrier Id') == 10 ).then (pl.lit('cBand')).otherwise(
                                              pl.when (pl.col ('gNB Type') == 0).then (pl.lit('mmW')). otherwise(pl.lit('FDD'))).alias ('freqType')])
  added_values = added_values.rename ( {"Value" : "nrCellId"} ) 
  
  VzMarketIdList =  added_values.select ('marketId').unique().to_series().to_list()
  print ('markets : ', VzMarketIdList)

# check the frequency total 
  
  unique_cells = added_values.select(['nrCellId', 'nbrGnbId', 'nbrCellId', 'Sector Id', 'Carrier Id', 'gNB Type', 'freqType' ]).unique()
    
   
  frequency_bands =  unique_cells.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))
  print ('Cells found in ', ravs_filename)
  print (frequency_bands)
  duplicates = all_cells.join (unique_cells, on='nrCellId', how = 'inner')
 
  print ('already found')
  print (duplicates.groupby (by = 'freqType').agg(pl.col( 'nrCellId').count()))  

  all_cells = pl.concat ([all_cells, unique_cells],  how = 'vertical').unique()
  
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
	gNB_files = list (p.glob ('gNB NR Cell Summary*.csv'))
	if len(gNB_files) > 0 : 
	   ravs_nokia_gNB_cells = pl.read_csv( gNB_files [0], separator = ';', eol_char = '\r')
	else : 
		print ('no files found at ', new_date, 'that match ', 'gNB NR Cell Summary*.csv')
		return 	
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
	rapper.to_excel (weekly_raw_data +  'nationwide_cells_SS_cBand_FDD.xlsx')

	global_result = pd.read_excel (base_dir + 'nationwide_cells_history.xlsx', 
								   sheet_name= 'hist total cells', 
								   dtype = {'Date' : str})

	global_result.index = global_result ['Date']
	path_split = weekly_raw_data.split('/') 
	yyyy, mm, dd = path_split [(len (path_split) - 2) ].split ('-')
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


def clean_eNB (date): 

    p = Path (date)
    eNB_files = list (p.glob ( 'eNB Releases via RAVS cloud*.csv'))
    try : 
        print ('reading current eNB from:', eNB_files[0] )
    except: 
        print (' no matching files found at: ', new_date)
        return

    eNB_source = pl.read_csv(eNB_files[0], separator = ';' , ignore_errors = True, eol_char = '\r')
    
    return eNB_source.filter ( (pl.col ('Area')  != 'Maintenance Area') &
            (pl.col('Planned NE Type') != 'fzmBTS') &  
            (pl.col ('eNB Operational State') == 'onAir') &
            (pl.col ('Market') != 'Westlake Lab'))   

def clean_gNB(date): 
    p = Path (date)
    gNB_files = list (p.glob ( 'gNB Releases via RAVS cloud*.csv'))
    try : 
        print ('reading current gNB from:', gNB_files[0] )
    except: 
        print (' no matching files found at: ', new_date)
        return 
    gNB_source = pl.read_csv(gNB_files [0],  separator = ";" ,  ignore_errors = True, eol_char = '\r')

    return gNB_source.filter ((pl.col ('gNB Operational State') == 'onAir') &  
                              (pl.col ('Planned NE Type') == 'sBTS') & 
                              (pl.col ('Market') != 'Westlake Lab') & 
                              (pl.col ('MRBTS ID') < 2560000) ) 


def four_week_delta (new_date, old_date): 
	current_eNB = clean_eNB (new_date)
	old_eNB = clean_eNB (old_date)  
	current_gNB = clean_gNB( new_date)
	old_gNB = clean_gNB(old_date)

	print ('current enb on Air: ', current_eNB.shape [0] )
	print ('current gnb on Air: ', current_gNB.shape[0] )
	print ('last Month enb on Air ', old_eNB.shape [0])
	print ('last Month gnb on Air: ', old_gNB.shape [0])
	delta_eNB = old_eNB.join (current_eNB, how = 'anti', left_on = 'MRBTS ID', right_on = 'MRBTS ID')
	delta_gNB = old_gNB.join (current_gNB, how = 'anti', left_on = 'MRBTS ID', right_on = 'MRBTS ID')
	unmatched_eNB = current_eNB.join (old_eNB, how = 'anti', left_on = 'MRBTS ID', right_on = 'MRBTS ID') 
	unmatched_gNB = current_gNB.join (old_gNB, how = 'anti', left_on = 'MRBTS ID', right_on = 'MRBTS ID') 
	print ('delta enb : ', delta_eNB.shape[0]  )
	print ('delta gnb : ', delta_gNB.shape[0]  )
	print ('new eNB (rename) : ', unmatched_eNB.shape [0])
	print ('new gNB (rename) : ', unmatched_gNB.shape [0])
    
	gNB_Adj_eNB_old = old_gNB.with_columns ((pl.col ('MRBTS ID') % 1000 + (pl.col ('MRBTS ID') // 10000) * 1000) .alias ('adj_eNB')) 
	site_delta = old_eNB.with_columns ((pl.col ('MRBTS ID').is_in (gNB_Adj_eNB_old ['adj_eNB'])).alias ('has 5G'), 
                                       (pl.col ('MRBTS ID').is_in (current_eNB ['MRBTS ID'])).alias ('not swapped'))
									   
	gNB_no_match = gNB_Adj_eNB_old.filter ( ~ pl.col('adj_eNB').is_in(old_eNB ['MRBTS ID']))
    
    # print (site_delta.schema)
	print ('old sites with 5G ', site_delta.groupby (by = 'has 5G').count())
	print ('old sites swapped ', site_delta.groupby (by = 'not swapped').count())
	print ('classic gNB without matching eNB',  gNB_no_match.shape [0])
	print ('classic gNB without matching eNB',  gNB_no_match.select ('MRBTS ID', 'Area', 'Region', 'Market', 'adj_eNB'))
    
    
	site_delta = site_delta.with_columns (  (pl.col ('has 5G') + pl.col ('not swapped') * 2 ).alias ('site change'))
	print (site_delta.groupby (by = 'site change').count().sort (by = 'site change'))
    
	site_delta.write_csv ('C:/Users/fn101139/OneDrive - Nokia/power BI dashboard/_current/site_changes.csv')
	delta_eNB.write_csv ('C:/Users/fn101139/OneDrive - Nokia/power BI dashboard/_current/4week_delta_eNB.csv')
	delta_gNB.write_csv ('C:/Users/fn101139/OneDrive - Nokia/power BI dashboard/_current/4week_delta_gNB.csv')
	
	previous_month_samsung_cells = pd.read_excel (last_month_raw_data + 'nationwide_cells_SS_cBand_FDD.xlsx', 
										   sheet_name='Sheet1')
	old_cells =  pl.DataFrame (previous_month_samsung_cells) 

	current_samsung_cells = pd.read_excel (weekly_raw_data + 'nationwide_cells_SS_cBand_FDD.xlsx', 
										   sheet_name='Sheet1')
	#%%
	new_cells = pl.DataFrame (current_samsung_cells) 
	delta_cells = new_cells.join (old_cells, how = 'anti', left_on = 'nrCellId', right_on = 'nrCellId')  

	print ('old total # cells = ', old_cells.shape[0])
	print ('current total # cells = ', current_samsung_cells .shape[0]) 
	print ('delta cells size:', delta_cells.shape[0])

	print ('starting write to file')
	delta_cells.write_csv ('C:/Users/fn101139/OneDrive - Nokia/power BI dashboard/_current/4week_delta_SS_cells.csv')







#main 

weekly_raw_data, last_month_raw_data = collect_dates( samsungConfig)

samsungConfig.set ('dir','rawData',  weekly_raw_data)

with open ( new_work_dir + '\\'+ 'samsungConfig.ini', 'w') as conf_file:
   samsungConfig.write (conf_file) 

delete_files(r'C:\Users\fn101139\OneDrive - Nokia\power BI dashboard\_current')
move_files()

process_nation_wide(weekly_raw_data)
store_nationwide_cells (weekly_raw_data, all_cells) 

four_week_delta(weekly_raw_data, last_month_raw_data)