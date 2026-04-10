#! /usr/bin/env python
import pandas as pd
import polars as pl
import numpy as np
import os
import shutil 
from pathlib import Path
import datetime
import polars.selectors as cs

# V5 : remove config file 
# V5 : remove dependency on local drive and feed only off one-drive power BI dashboard 
# v5 : all directory path and now Path objects 
     
base_dir =  Path ('C:/Users/fn101139/OneDrive - Nokia/power BI dashboard/')
current_dir = base_dir / '_current'
four_weeks_back_dir = base_dir 
source_file_dir =  Path ('C:/Users/fn101139/Downloads/')

def last_sunday () : 
	current_day = datetime.date.today() 
	count_day_back_to_Sunday =   datetime.timedelta (days = current_day.weekday() + 1)
	sunday_date = current_day - count_day_back_to_Sunday
	print (sunday_date)
	return sunday_date.isoformat() 

def four_weeks_back (current_date):
   sample_date =  datetime.date.fromisoformat (current_date)
   # for the power BI storage the backup is on saturday, so you have to add 1 day to the 4 week 
   four_weeks = datetime.timedelta (days = 28 + 1)
   fourweekback_date = sample_date - four_weeks 
   return  fourweekback_date.isoformat()

def collect_dates ():
	
	suggested_date = last_sunday() 	
	new_current_date = input ('current date : ' + suggested_date + ' Overwrite (enter to accept)?')  
	current_date = new_current_date if (len (new_current_date) != 0) else suggested_date

	four_weeks_back_date = four_weeks_back(current_date)
	
	return  current_date, four_weeks_back_date

def delete_files (target_dir) :
	print ("deleting : ".format (target_dir) )

	
	report = list (target_dir.glob ('?NB Releases via RAVS cloud_*.csv'))
	print ('found matching files: {}'.format( report))
	for f in report:
		print ('remove  {}'.format (f)) 
		os.remove (f)
	
	report = list (target_dir.glob ('gNB NR Cell Summary_*.csv')) 
	print ('found matching files: {}'.format( report))

	for f in report:
		print ('remove  {}'.format (f)) 
		os.remove (f)	
		
	try :
		print ("now removing : ", (target_dir / 'allNetwork_x2linkStat.csv')) 
		os.remove ((target_dir / 'allNetwork_x2linkStat.csv'))
	except :
		print ('file already removed') 	



def move_RAV_files (source, target_dir) : 
	
	
	
	report = list (source.glob ('upstate_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	print ('moving ', latest_version)
	shutil.copy2 (latest_version, target_dir / 'report (1).csv' )
	
	report = list (source.glob ('south_east_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, (target_dir /  'report (2).csv' ))
	
	report = list (source.glob ('Washington_baltimore*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, (target_dir /  'report (3).csv' ))
	
	report = list (source.glob ('mountain_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version,( target_dir / 'report (4).csv' ))
	
	report = list (source.glob ('great_lakes_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, (target_dir /  'report (5).csv' ))
	
	report = list (source.glob ('Tri_state_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, (target_dir /  'report (6).csv' ))
	
	report = list (source.glob ('New_york_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, (target_dir /  'report (7).csv' ))
	
	report = list (source.glob ('south_central_nbr_cell*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, (target_dir /  'report (8).csv' ))		
    
	report = list (source.glob ('eNB Releases via RAVS cloud_*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, target_dir  ) 	
	
	report = list (source.glob ('gNB Releases via RAVS cloud_*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, target_dir  ) 	
	
	report = list (source.glob ('gNB NR Cell Summary_*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, target_dir  )
	
	report = list (source.glob ('allNetwork_x2linkStat*.csv'))
	latest_version = max ([f for f in report], key = lambda item: item.stat().st_ctime) 
	shutil.copy2 (latest_version, (target_dir / 'allNetwork_x2linkStat.csv' ))  	
	
          		
     


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
    
   
  frequency_bands =  unique_cells.group_by (by = 'freqType').agg(pl.col( 'nrCellId').count().alias ('#cells'))
  print ('Cells found in ', ravs_filename)
  print (frequency_bands)
  duplicates = all_cells.join (unique_cells, on='nrCellId', how = 'inner')
 
  print ('already found')
  print (duplicates.group_by (by = 'freqType').agg(pl.col( 'nrCellId').count()))  

  all_cells = pl.concat ([all_cells, unique_cells],  how = 'vertical').unique()
  
#  for mkt in VzMarketIdList  :
#      added_values.filter(pl.col ('marketId')  ==   mkt).write_csv (weekly_raw_data +  "pl_eNB_per_" + str (mkt) + ".csv")
      
def process_nation_wide (source): 

  
  report_files = list (source.glob('report*.csv')) 
  print ('files found : ', report_files)       
 
  for f in report_files :
     read_process_region (f)       


def store_nationwide_cells(current_date, all_cells) : 
     
	# compare against Nokia Cells, no additional enforcement 
	current_dir
	gNB_files = list (current_dir.glob ('gNB NR Cell Summary*.csv'))
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
 	
	frequency_bands = all_unique_cells.group_by (by = ['freqType', 'isNokia']).agg(pl.col( 'nrCellId').count().alias ('#cells'))
	print ('cells found per vendor and band:')
	print (frequency_bands.sort)

	rapper = all_cells.to_pandas()
	rapper.to_excel ( (current_dir /  'nationwide_cells.xlsx'))

	cells_SS_only = all_cells.filter ((pl.col('freqType')  != 'mmW') & (~ pl.col('isNokia')))
	rapper = cells_SS_only.to_pandas()
	rapper.to_excel ((current_dir / 'nationwide_cells_SS_cBand_FDD.xlsx'))

	global_result = pd.read_excel ((base_dir / 'nationwide_cells_history.xlsx'), 
								   sheet_name= 'hist total cells', 
								   dtype = {'Date' : str})

	global_result.index = global_result ['Date']
	print (" check " + current_date) 
	new_data = global_result ['Date'].str.contains (current_date) 

	if (new_data.any()) :
		print ('no update required in global result file nationwide_cells_history.xlsx')
		print ('calculated....')
		print ('cBand       ', frequency_bands.filter ((pl.col('freqType') == 'cBand') & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD samsung ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD Nokia   ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( pl.col('isNokia'))) [0,2])		
	else :
	   
		global_result.at [current_date, 'Date'] = current_date
		global_result.at [current_date, 'cBand']  =       frequency_bands.filter ((pl.col('freqType') == 'cBand') & ( ~pl.col('isNokia'))) [0,2]
		global_result.at [current_date, 'FDD Samsung'] =  frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( ~pl.col('isNokia'))) [0,2]
		global_result.at [current_date, 'FDD Nokia']  =   frequency_bands.filter ((pl.col('freqType') == 'FDD')   & (  pl.col('isNokia'))) [0,2]
		global_result.at [current_date, 'mmW Samsung'] =  frequency_bands.filter ((pl.col('freqType') == 'mmW')   & ( ~pl.col('isNokia'))) [0,2]                                           
		global_result.at [current_date, 'mmW Nokia']  =   frequency_bands.filter ((pl.col('freqType') == 'mmW')   & (  pl.col('isNokia'))) [0,2]
		print ('adding....')
		print ('cBand       ', frequency_bands.filter ((pl.col('freqType') == 'cBand') & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD samsung ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( ~pl.col('isNokia'))) [0,2])
		print ('FDD Nokia   ', frequency_bands.filter ((pl.col('freqType') == 'FDD')   & ( pl.col('isNokia'))) [0,2])
	
	global_result.to_excel( (base_dir / 'nationwide_cells_history.xlsx'), 
								   sheet_name= 'hist total cells', index= False )
	  
	print ('end conversion : ', pd.Timestamp.now ())
	print ('end write : ', pd.Timestamp.now ())


def clean_eNB (source): 

   
    eNB_files = list (source.glob ( 'eNB Releases via RAVS cloud*.csv'))
    try : 
        print ('reading current eNB from:', eNB_files[0] )
    except: 
        print (' no matching files found at: ', source)
        return

    eNB_source = pl.read_csv(eNB_files[0], separator = ';' , ignore_errors = True, eol_char = '\r')
    
    return eNB_source.filter ( (pl.col ('Area')  != 'Maintenance Area') &
            (pl.col('Planned NE Type') != 'fzmBTS') &  
            (pl.col ('eNB Operational State') == 'onAir') &
            (pl.col ('Market') != 'Westlake Lab'))   

def clean_gNB(source): 
  
    gNB_files = list (source.glob ( 'gNB Releases via RAVS cloud*.csv'))
    try : 
        print ('reading current gNB from:', gNB_files[0] )
    except: 
        print (' no matching files found at: ', source)
        return 
    gNB_source = pl.read_csv(gNB_files [0],  separator = ";" ,  ignore_errors = True, eol_char = '\r')

    return gNB_source.filter ((pl.col ('gNB Operational State') == 'onAir') &  
                              (pl.col ('Planned NE Type') == 'sBTS') & 
                              (pl.col ('Market') != 'Westlake Lab') & 
                              (pl.col ('MRBTS ID') < 2560000) ) 


def four_week_delta (new_date, old_date): 
	old_dir =  base_dir / old_date
	current_eNB = clean_eNB (current_dir)
	old_eNB = clean_eNB (old_dir)  
	current_gNB = clean_gNB( current_dir)
	old_gNB = clean_gNB(old_dir)

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
	print ('old sites with 5G ', site_delta.group_by (by = 'has 5G').count())
	print ('old sites swapped ', site_delta.group_by (by = 'not swapped').count())
	print ('classic gNB without matching eNB',  gNB_no_match.shape [0])
	print ('classic gNB without matching eNB',  gNB_no_match.select ('MRBTS ID', 'Area', 'Region', 'Market', 'adj_eNB'))
    
    
	site_delta = site_delta.with_columns (  (pl.col ('has 5G') + pl.col ('not swapped') * 2 ).alias ('site change'))
	print (site_delta.group_by (by = 'site change').count().sort (by = 'site change'))
    
	site_delta.write_csv (os.path.join (current_dir, 'site_changes.csv'))
	delta_eNB.write_csv (os.path.join (current_dir, '4week_delta_eNB.csv'))
	delta_gNB.write_csv (os.path.join (current_dir, '4week_delta_gNB.csv'))
	
	previous_month_samsung_cells = pd.read_excel ((old_dir / 'nationwide_cells_SS_cBand_FDD.xlsx'), 
										   sheet_name='Sheet1')
	old_cells =  pl.DataFrame (previous_month_samsung_cells) 

	current_samsung_cells = pd.read_excel ((current_dir / 'nationwide_cells_SS_cBand_FDD.xlsx'), 
										   sheet_name='Sheet1')
	#%%
	new_cells = pl.DataFrame (current_samsung_cells) 
	delta_cells = new_cells.join (old_cells, how = 'anti', left_on = 'nrCellId', right_on = 'nrCellId')  

	print ('old total # cells = ', old_cells.shape[0])
	print ('current total # cells = ', current_samsung_cells .shape[0]) 
	print ('delta cells size:', delta_cells.shape[0])

	print ('starting write to file')
	delta_cells.write_csv ((current_dir / '4week_delta_SS_cells.csv'))







#main 

current_date, four_week_back  = collect_dates( )


delete_files(current_dir)
move_RAV_files(source_file_dir, current_dir)

process_nation_wide(current_dir)
store_nationwide_cells (current_date, all_cells) 

four_week_delta(current_date, four_week_back)