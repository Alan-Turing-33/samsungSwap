#! /usr/bin/env python
import pandas as pd
import numpy as np
import configparser
import os

samsungConfig =  configparser.ConfigParser()
samsungConfig.read ('samsungConfig.ini')
weeklyRawData = samsungConfig ['dir']['rawData'] 

print ('start conversion : ', pd.Timestamp.now ())
# CSV files to parse

# Coloumns of interest and indices
# C: Global eNodeB ID - 2
# I: Full Object Path - 8 --> get LNCEL and LNRELGNBCELL value
# K: Value - 10

two_Power_14 = 2 ** 14

def read_process_region (ravs_filename) :
  result = pd.DataFrame ()
  print ("processing : ",  ravs_filename)
               
  for chunk in pd.read_csv(ravs_filename, skiprows =5, usecols= ['Global eNodeB ID', 'Full Object Path', 'Value'],  chunksize = 100000):
  
      temp = chunk['Full Object Path'].str.split("/", expand = True )
      chunk ['lncel'] = temp[2].str.split ("-", expand = True) [1]
      chunk ['lncel'] = chunk ['lncel'].astype(int)
      chunk ['lnRelGnbCell']= temp[3].str.split ("-", expand = True ) [1]  
      chunk ['nbrGnbId']  = chunk['Value'] // two_Power_14
      chunk ['nbrCellId']  = chunk['Value'] % two_Power_14
      chunk ['marketId'] = np.where ((chunk['Global eNodeB ID'] // 1000) < 300, (chunk['Global eNodeB ID'] // 1000), (chunk['Global eNodeB ID'] // 1000) - 300)
      chunk ['freqType'] =  np.where ((chunk['nbrGnbId']%10000 > 9000) , "cmW" , "mmW" ) 
      chunk ['freqType'] =  np.where ((chunk['nbrCellId']%16 == 10) , "cBand" , chunk ['freqType'])
      chunk ['uniqueSector'] = (chunk ['Global eNodeB ID'] * 100) + (chunk ['lncel'] // 10)
      result = pd.concat ([result , chunk], ignore_index=True)  

  result.rename (columns = {"Value" : "nrCellId"}, inplace=True ) 
  VzMarketIdList = result ['marketId'].unique().tolist()
  print ('markets : ', VzMarketIdList)

  for mkt in VzMarketIdList :
      mktresult = result[result.marketId ==   mkt]
      mktresult.to_csv(weeklyRawData +  "eNB_per_" + str (mkt) + ".csv")
 
report_files = []

for candidate in os.listdir(weeklyRawData):
    if (os.path.isfile(os.path.join(weeklyRawData, candidate)) and 
        (('report' in candidate) or ('LNRELGNBCELL_nrCellId' in candidate))):
         report_files.append(candidate)
         
print ('files found : ', report_files)       

for f in report_files :
     read_process_region (weeklyRawData + f)       
                   
  
print ('end conversion : ', pd.Timestamp.now ())
print ('end write : ', pd.Timestamp.now ())
