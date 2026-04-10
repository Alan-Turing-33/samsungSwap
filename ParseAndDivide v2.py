#! /usr/bin/env python
import pandas as pd
import numpy as np
import configparser
import os


wdir = os.getcwd()
print ('reading inti', wdir + '\samsungConfig.ini')
samsungConfig =  configparser.ConfigParser()
samsungConfig.read (wdir + '\samsungConfig.ini')
weeklyRawData = samsungConfig ['dir']['rawData'] 

print ('start conversion : ', pd.Timestamp.now ())
# CSV files to parse

# Coloumns of interest and indices
# C: Global eNodeB ID - 2
# I: Full Object Path - 8 --> get LNCEL and LNRELGNBCELL value
# K: Value - 10

two_Power_14 = 2 ** 14

def read_process_region (ravs_filename) :
  global cBand_global
  global cmW_global   
  print ("processing : ",  ravs_filename)
  result = pd.read_csv(ravs_filename, skiprows =5, usecols= ['eNodeB Group', 'Global eNodeB ID', 'Full Object Path', 'Value'])
  print ('remove Decommissioned ENB Group' , sum ( result ['eNodeB Group'] == 'Decommissioned ENB Group'))
  result.drop (result[result ['eNodeB Group'] == 'Decommissioned ENB Group'].index, inplace =True)
  print ('remove Decommissioned Group' , sum ( result ['eNodeB Group'] == 'Decommissioned Group'))
  result.drop (result[result ['eNodeB Group'] == 'Decommissioned Group'].index, inplace =True)

  temp = result ['Full Object Path'].str.split("/", expand = True )
  if (temp.shape [1] > 0):
    result ['lncel'] = temp[2].str.split ("-", expand = True) [1]  
    result ['lncel'] = result ['lncel'].astype(int)
    result ['lnRelGnbCell']= temp[3].str.split ("-", expand = True ) [1]               
  
  result ['nbrGnbId']  = result ['Value'] // two_Power_14
  result ['nbrCellId']  = result['Value'] % two_Power_14
  result ['marketId'] = np.where ((result['Global eNodeB ID'] // 1000) < 300, (result['Global eNodeB ID'] // 1000), (result['Global eNodeB ID'] // 1000) - 300)
  result ['freqType'] =  np.where ((result['nbrGnbId']%10000 > 9000) , "cmW" , "mmW" ) 
  result ['freqType'] =  np.where ((result['nbrCellId']%16 == 10) , "cBand" , result ['freqType'])
  result.rename (columns = {"Value" : "nrCellId"}, inplace=True ) 
  
  VzMarketIdList = result ['marketId'].unique().tolist()
  print ('markets : ', VzMarketIdList)

# check the frequency total 

  cband_cell = set (result.loc [ result ['freqType'] == 'cBand', 'nrCellId']) 
  cmW_cell = set(result.loc [ result ['freqType'] == 'cmW', 'nrCellId'])

  print ('cBand cells found :', len (cband_cell))
  print ('cmW cells found :', len (cmW_cell))

  print ('cBand already found: ',  len (cband_cell & cBand_global))
  print ('cmW already found: ',  len (cmW_cell & cmW_global))
  cBand_global = cBand_global | cband_cell
  cmW_global = cmW_global | cmW_cell
  
  mkt_range = list (set (result.marketId))
  for mkt in mkt_range  :
      mktresult = result[result.marketId ==   mkt]
      mktresult.to_csv(weeklyRawData +  "eNB_per_" + str (mkt) + ".csv")
 
report_files = []

for candidate in os.listdir(weeklyRawData):
    if (os.path.isfile(os.path.join(weeklyRawData, candidate)) and 
        (('report' in candidate) or ('LNRELGNBCELL_nrCellId' in candidate))):
         report_files.append(candidate)
         
print ('files found : ', report_files)       


cBand_global = set () 
cmW_global = set() 
for f in report_files :
     read_process_region (weeklyRawData + f)       
                   
print ('total cBand cells found :', len (cBand_global ))
print ('total cmW cells found :', len (cmW_global))
  
print ('end conversion : ', pd.Timestamp.now ())
print ('end write : ', pd.Timestamp.now ())
