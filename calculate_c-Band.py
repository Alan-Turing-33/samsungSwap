#! /usr/bin/env python


import pandas as pd
import numpy as np
import configparser
import folium 
samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')

weekly_raw_data = samsungConfig ['dir']['rawData'] 

#%%




resultFileName = weekly_raw_data + 'c_band_per_eNB.xlsx'
cmWaveAuditFile = weekly_raw_data + 'gnb_4_cmWave.csv'
mmWaveAuditFile = weekly_raw_data + 'gnb_4_mmWave.csv'

unique_cells_nationwide = pd.DataFrame(columns= ['Global eNodeB ID', 'Full Object Path', 'nrCellId', 'lncel', 'lnRelGnbCell', 
                                                 'nbrGnbId', 'nbrCellId', 'marketId', 'freqType', 'uniqueSector', 'inMarket', 
                                                 'Nokia', 'cBandNokia', '#gNB cBand Sectors', '#gNB cm Sectors',])


result = pd.read_excel(resultFileName,   sheet_name = 'Sheet1')


    

def cell_count (mkt, market_data): 
    
    market_data ['freqType'] =  np.where((market_data['nbrGnbId']%10000 > 9000) , "cmW" , "mmW" ) 
    market_data ['freqType'] =  np.where((market_data['nbrCellId']%16 == 10) , "cBand" , market_data ['freqType']) 
       
    market_data ['nbrGnbId'] = market_data ['nbrGnbId'].astype (str)
    market_data ['nbrGnbId'] = market_data ['nbrGnbId'].astype (int)
    
    temp_result = market_data.groupby(['Global eNodeB ID', 'freqType']) ['nbrCellId'].nunique()
    print ( temp_result)                
    return pd.DataFrame (temp_result) 
    
 


def analyticsPerMarket (marketId):
    
    print ('start analysis for ',   marketId, ' time : ', pd.Timestamp.now () )
    try:           
        market_data = pd.read_csv(weekly_raw_data + "eNB_per_" +  str (marketId) + ".csv")
    except:
        print (str(marketId) , ' file not found')
        return
    for c in market_data.columns :
        if c.startswith ('Unnamed:'):
            market_data.drop (c,axis = 1, inplace = True) 
    if "Value" in market_data.columns : 
       market_data.rename (columns = {"Value" : "nrCellId"}, inplace=True ) 
        
    freq_data_eNB =  cell_count (marketId, market_data)
    freq_data_eNB.to_csv (weekly_raw_data + "cells_per_eNB" +  str (marketId) + ".csv")     
        
        
 # end of main function        

for mkt in  [78, 79, 80, 81,82, 84, 85, 86,87, 88, 89, 90, 91, 96, 96, 97, 98, 99, 100, 101, 102, 
             106, 107, 107, 109, 110, 111, 112, 113, 114, 115, 117, 120, 121, 122, 123, 124, 125, 
             126, 127, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140,
             180, 181, 182, 184, 185, 186, 241, 242, 243, 244, 245, 246, 247, 250, 251, 252, 253, 
              254]:
    if type (mkt) == int :
      analyticsPerMarket (mkt)       

# print (market_result)
# print (market_result.info) 
