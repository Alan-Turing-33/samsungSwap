#! /usr/bin/env python


import pandas as pd
import numpy as np
import configparser

samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')

weekly_raw_data = samsungConfig ['dir']['rawData'] 

base_dir = samsungConfig ['dir']['base'] 

# CSV files to parse


resultFileName = weekly_raw_data + 'sectorResult_permarket.xlsx'

unique_cells_nationwide = pd.DataFrame(columns= ['Global eNodeB ID', 'Full Object Path', 'nrCellId', 'lncel', 'lnRelGnbCell', 
                                                 'nbrGnbId', 'nbrCellId', 'marketId', 'freqType', 'uniqueSector', 'inMarket', 
                                                 'Nokia', 'cBandNokia', '#gNB cBand Sectors', '#gNB cm Sectors',])


market_result = pd.read_excel(resultFileName,   sheet_name = 'Sheet1', dtype = { 'Market' : int})

ravs_gNB = pd.read_csv( weekly_raw_data  + 'gNB NR Cell Summary.csv', sep = ';', on_bad_lines = 'warn')

ravs_cmWave = set (ravs_gNB.loc [ (ravs_gNB['Planned NE Type' ] == '5gClassicalBTS') | 
                                  (ravs_gNB['Planned NE Type' ] == 'sBTS'), 'MRBTS ID' ])
print (' classic gNB found : ' , len (ravs_cmWave))

ravs_mmWave = set (ravs_gNB.loc [ (ravs_gNB['gNB Operational State' ] == 'enabled') & 
                                  (ravs_gNB['Planned NE Type' ] == '5gCU') , 'MRBTS ID' ])
print (' mmWave gNB found : ',  len (ravs_mmWave))



for c in market_result.columns :
        if c.startswith ('Unnamed:'):
            market_result.drop (c,axis = 1, inplace = True) 


VzMarketIdList = market_result['Market'].tolist()
market_result.set_index('Market', inplace=True)

old_result = market_result.columns

#%%    
def IsNokia(gnb):
    testValue = int(gnb)
    return  (testValue  in ravs_cmWave ) or (testValue in ravs_mmWave)
95 * 1.3  
def IsInMarket (gNB,mkt):
    a = str (gNB) 
    b = str (mkt)
    return a.startswith(b)   

def extractFreqType (gNB):
# uses the 4 digit from the right to check for vRAN 1.0 or other. assumption vRAN 1.0  = 0 , cmwave and       
#   if (type(gNB) != int) :
#       print (type (gNB))
    
   if gNB%10000 > 9000:
     value = "cmW" 
   else :
      value = "mmW"
   return value      

def convertHEX (identifier):
    return str(hex(identifier)) 
               
def isCBAND (identifier):
   return identifier [-1:] == "a"

def prepareMarketdata (mkt, market_data): 
    
    market_data ['freqType'] =  np.where((market_data['nbrGnbId']%10000 > 9000) , "cmW" , "mmW" ) 
    market_data ['freqType'] =  np.where((market_data['nbrCellId']%16 == 10) , "cBand" , market_data ['freqType']) 
       
    market_data ['nbrGnbId'] = market_data ['nbrGnbId'].astype (str)
    market_data ['inMarket'] = (market_data ['nbrGnbId'].str.startswith(str (mkt)))
    market_data ['nbrGnbId'] = market_data ['nbrGnbId'].astype (int)
    
    if ('vendor' in market_data.columns) :
        market_data.drop ('vendor', axis = 1,  inplace = True)
    
    market_data ['Nokia'] = market_data ['nbrGnbId'].apply(IsNokia)
    market_data ['uniqueSector'] = (market_data ['Global eNodeB ID'] * 100) + (market_data ['lncel'] // 10)
#    market_data ['uniqueSector'] = np.where (market_data ['lncel'] > 10,  
#                                             (market_data ['Global eNodeB ID'] * 100 + market_data ['lncel'] // 10), 
#                                             (market_data ['Global eNodeB ID'] * 100 + market_data ['lncel']))


    market_data ['cBandNokia'] =  (market_data['freqType'] == 'cBand') &  market_data['Nokia'] 
    market_data ['Nokia'] =  np.where ( (market_data['freqType'] == 'cBand'), False,  market_data['Nokia'])
    market_data ['Nokia'] = market_data ['Nokia'].astype ('boolean')
    
    
    
def  AnalyzeLTESector(marketId, market_data): 
    
        market_result.at [marketId, '# eNB']  = market_data ['Global eNodeB ID'].nunique()  
        market_result.at [marketId, '# eNB Sector'] = market_data['uniqueSector'].nunique()
    
        market_result.at [marketId, 'NR rel cm'] = market_data.loc [(market_data ['freqType'] == 'cmW') , 'uniqueSector'].nunique()
        market_result.at [marketId, 'NR rel mm'] = market_data.loc [(market_data ['freqType'] == 'mmW') , 'uniqueSector'].nunique()     
        market_result.at [marketId, 'NR rel CBand'] = market_data.loc [(market_data ['freqType'] == 'cBand') , 'uniqueSector'].nunique() 
        market_result.at [marketId, 'NR rel cm Nokia'] = market_data.loc [(market_data ['freqType'] == 'cmW') & (market_data.Nokia)  , 'uniqueSector'].nunique()  
        market_result.at [marketId, 'NR rel mm Nokia']= market_data.loc [(market_data ['freqType'] == 'mmW') & (market_data.Nokia )  , 'uniqueSector'].nunique()  
 
def  Analyze5GCell(marketId, market_data): 
        global unique_cells_nationwide
        unique_cells = market_data.drop_duplicates(['nrCellId']) 
        unique_cells = unique_cells [unique_cells ['inMarket']]
        market_result.at [marketId, 'Ngb gNB'] = market_data.loc [(market_data.inMarket), 'nbrGnbId'].nunique()
       
        unique_cells  ['Nokia'] = unique_cells ['Nokia'].astype ('boolean')
        market_result.at [marketId, 'Ngb cell ID'] = unique_cells.shape [0]
        market_result.at [marketId, '5G cell CBand Nokia'] = sum (unique_cells.cBandNokia)
     
        market_result.at [marketId, '5G cell cm Nokia'] = sum ((unique_cells ['freqType'] == 'cmW') & (unique_cells.Nokia))
        market_result.at [marketId, '5G cell cm Samsung'] = sum ((unique_cells ['freqType'] == 'cmW') & (~ unique_cells.Nokia))

        market_result.at [marketId, '5G cell mm Nokia'] = sum ((unique_cells ['freqType'] == 'mmW') & (unique_cells.Nokia))
        market_result.at [marketId, '5G cell mm Samsung'] = sum ((unique_cells ['freqType'] == 'mmW') & ( ~unique_cells.Nokia))
        
        market_result.at [marketId, '5G cell CBand'] = sum ((unique_cells ['freqType'] == 'cBand'))  
        
        ##################################

        cBand_cells = unique_cells.loc [(unique_cells ['freqType'] == 'cBand'),  ['nbrGnbId','nrCellId'] ]
        gNB_cBand = cBand_cells.groupby ('nbrGnbId').count()
        gNB_cBand.reset_index (inplace = True)
        
        gNB_cBand.rename (columns = {'nrCellId' : '#gNB cBand Sectors', 'index' : 'nbrGnbId' }, inplace = True)
        
        market_result.at [marketId, '# cBand gNB > 10 '] = sum ((gNB_cBand ['#gNB cBand Sectors'] > 10))
        market_result.at [marketId, '# 4/2 Sector gNB cBand'] = sum ((gNB_cBand ['#gNB cBand Sectors'] <=4 ))       
        market_result.at [marketId, '# cBand gNB'] = gNB_cBand.shape [0]
        market_result.at [marketId, 'cBand gNB max size'] = gNB_cBand ['#gNB cBand Sectors'].max()  
                             
        unique_cells = pd.merge (unique_cells, gNB_cBand, how ='left', on = 'nbrGnbId')
         
         ###################################
        cmW_SS_cells = unique_cells.loc [((unique_cells ['freqType'] == 'cmW') & (~unique_cells.Nokia)),  ['nbrGnbId','nrCellId'] ]
        gNB_cmW_SS = cmW_SS_cells.groupby ('nbrGnbId').count()
        gNB_cmW_SS.reset_index (inplace = True)
        
        gNB_cmW_SS.rename (columns = {'nrCellId' : '#gNB cm Sectors', 'index' : 'nbrGnbId' }, inplace = True)
        
        market_result.at [marketId, '# SS n5/n2 gNB > 10 '] = sum ((gNB_cmW_SS ['#gNB cm Sectors'] > 10))
        market_result.at [marketId, '# SS 4/2 Sector gNB n5/n2'] = sum ((gNB_cmW_SS ['#gNB cm Sectors'] <=4 ))       
        market_result.at [marketId, '# SS n5/2 gNB'] = gNB_cmW_SS.shape [0]
        market_result.at [marketId, 'SS n5/n2 gNB max size'] = gNB_cmW_SS ['#gNB cm Sectors'].max()  
       
        unique_cells = pd.merge (unique_cells, gNB_cmW_SS, how ='left', on = 'nbrGnbId')
         ###################################
        
        unique_cells.rename (columns = {'nrCellId_y' : '#gNB cm Sectors'}, inplace = True)
        
        unique_cells_nationwide = pd.concat ([unique_cells_nationwide, unique_cells])
        print ( ' all unique cBand cell :',  sum (((unique_cells_nationwide ['freqType'] == 'cBand'))))
        
        bm_gNB = sum ((unique_cells [ 'freqType'] == 'cmW') & (~unique_cells.Nokia) & (unique_cells [ '#gNB cm Sectors'] <= 4))
        cloud_gNB = sum ((unique_cells [ 'freqType'] == 'cmW') & (~unique_cells.Nokia) & (unique_cells [ '#gNB cm Sectors'] > 10))
        unknown_gNB = sum ((unique_cells [ 'freqType'] == 'cmW') & (~unique_cells.Nokia) & (unique_cells [ '#gNB cm Sectors'] < 10) &  
                           (unique_cells [ '#gNB cm Sectors'] > 4))  
        market_result.at [marketId, '#n5/n2 SS Sectors served by < 4 sector gNB '] = bm_gNB
        market_result.at [marketId, '#n5/n2 SS Sectors served by > 10 sector gNB '] = cloud_gNB 
        market_result.at [marketId, '#n5/n2 SS Sectors served by > unknown gNB '] = unknown_gNB
        mmW_cells = unique_cells.loc [(unique_cells ['freqType'] == 'mmW'),  ['nbrGnbId','nrCellId'] ]
        
        cBand_gNB = set ( cBand_cells ['nbrGnbId']) 
        cmW_gNB = set  (cmW_SS_cells ['nbrGnbId']) 
        mmW_gNB = set (mmW_cells [['nbrGnbId']] )
        multiFreq = len (cBand_gNB & cmW_gNB) 
        cBandOnly = len (cBand_gNB - cmW_gNB)
        multiFreqmmW = len (mmW_gNB & ( cBand_gNB | cmW_gNB)) 
        market_result.at [marketId, '# multi Freq gNB'] = multiFreq
        market_result.at [marketId, '# multi Freq gNB mmW'] = multiFreqmmW
        market_result.at [marketId, '# cBand only gNB'] = cBandOnly



def compareLTECoverage (marketId, market_data) :   
     cmW_Sectors = set (market_data.loc [market_data ['freqType'] == 'cmW', 'uniqueSector'])
     cBand_Sectors = set (market_data.loc [market_data ['freqType'] == 'cBand', 'uniqueSector'])
     mmW_Sectors  = set (market_data.loc [market_data ['freqType'] == 'mmW', 'uniqueSector'])
     temp =  (cBand_Sectors - cmW_Sectors) 
     market_result.at [marketId, '# cBand only Sector'] = len (temp) 
     temp =  (cmW_Sectors - cBand_Sectors ) 
     market_result.at [marketId, '# n5/n2 only Sector'] = len (temp) 
     temp = (cmW_Sectors & cBand_Sectors )
     market_result.at [marketId, '# n5/n2 & cBand Sector'] = len (temp) 
     temp = (cmW_Sectors - cBand_Sectors - mmW_Sectors)
     market_result.at [marketId, '# cBand only Sector no mmW'] = len (temp) 
     temp =  (cmW_Sectors - cBand_Sectors - mmW_Sectors) 
     market_result.at [marketId, '# n5/n2 only Sector no mmW'] = len (temp) 
     temp = (cmW_Sectors & cBand_Sectors - mmW_Sectors)
     market_result.at [marketId, '# n5/n2 & cBand Sector no mmW'] = len (temp) 
     
     
     
     
     cBand_data = market_data.loc [(market_data ['freqType'] == 'cBand') & market_data.inMarket]
     cmW_data = market_data.loc [(market_data ['freqType'] == 'cmW') & (~ market_data.Nokia) & market_data.inMarket]
    
     group_cBAND_cell = cBand_data.groupby ('nrCellId')
     eNB_per_cBand_Cell =  group_cBAND_cell ['uniqueSector'].nunique()
     market_result.at [marketId, 'Cband cell > 50 LTE sector'] = (eNB_per_cBand_Cell > 50).sum()
     market_result.at [marketId, 'Cband cell max LTE sector'] = eNB_per_cBand_Cell.max()
     
     group_cmW_cell = cmW_data.groupby ('nrCellId')
     eNB_per_cmW_Cell =  group_cmW_cell ['uniqueSector'].nunique()
     market_result.at [marketId, 'n5/n2 cell > 50 LTE sector'] = (eNB_per_cmW_Cell > 50).sum()
     market_result.at [marketId, 'n5/n2 cell max LTE sector'] = eNB_per_cmW_Cell.max()



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
        
    prepareMarketdata(marketId, market_data)
    AnalyzeLTESector(marketId, market_data)
    Analyze5GCell(marketId, market_data)    
    compareLTECoverage(marketId, market_data)     
         
        
    market_data.to_csv(weekly_raw_data + "eNB_per_" +  str (marketId) + ".csv")
        
        
 # end of main function        

for mkt in  VzMarketIdList:
    if type (mkt) == int :
      analyticsPerMarket (mkt)       

# print (market_result)
# print (market_result.info) 

market_result ['5G cell cm'] = market_result ['5G cell cm Samsung'] + market_result ['5G cell cm Nokia']
market_result ['5G cell mm'] = market_result ['5G cell mm Samsung'] + market_result ['5G cell mm Nokia']
market_result ['5G cell C-band wo boarder cm ratio'] = market_result ['5G cell CBand'] / market_result ['5G cell cm']


unique_cells_nationwide ['Nokia'] = unique_cells_nationwide ['Nokia'].astype ('boolean')

#%% 


# 
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
   global_result.at [snapshot_date, 'cBand']  = sum (unique_cells_nationwide ['freqType'] == 'cBand')
   global_result.at [snapshot_date, 'cmW Samsung'] =  sum ((unique_cells_nationwide ['freqType'] == 'cmW') & (~ unique_cells_nationwide.Nokia))                                                 
   global_result.at [snapshot_date, 'cmW Nokia']  = sum ((unique_cells_nationwide ['freqType'] == 'cmW') & (unique_cells_nationwide.Nokia))
   global_result.at [snapshot_date, 'mmW Samsung'] =  sum ((unique_cells_nationwide ['freqType'] == 'mmW') & (~ unique_cells_nationwide.Nokia))                                                 
   global_result.at [snapshot_date, 'mmW Nokia']  = sum ((unique_cells_nationwide ['freqType'] == 'mmW') & (unique_cells_nationwide.Nokia))
    

print ( 'all unique Nokia cell for mm :',  sum (((unique_cells_nationwide ['freqType'] == 'mmW')   & (unique_cells_nationwide.Nokia))))
print ( ' all unique Samsung cell for mm :',  sum (((unique_cells_nationwide ['freqType'] == 'mmW') &   ( ~ unique_cells_nationwide.Nokia))))

print ( ' all unique Nokia cell for cm :',  sum (((unique_cells_nationwide ['freqType'] == 'cmW') & (unique_cells_nationwide.Nokia))))
print ( ' all unique Samsung cell for cm :',  sum (((unique_cells_nationwide ['freqType'] == 'cmW') & (~ unique_cells_nationwide.Nokia))))
print ( ' all unique cBand cell :',  sum (((unique_cells_nationwide ['freqType'] == 'cBand'))))

global_result.to_excel(base_dir + 'nationwide_cells_history.xlsx', 
                               sheet_name= 'hist total cells', index= False )
#%%       
market_result.to_excel ( resultFileName)

unique_cells_nationwide.to_excel (weekly_raw_data +  'nationwide_cells.xlsx')


cells_SS_only = unique_cells_nationwide [~unique_cells_nationwide.Nokia & (unique_cells_nationwide.freqType != 'mmW')]

reduced_active_cells_file_Name = weekly_raw_data +  'nationwide_cells_SS_cBand_cmW.xlsx'
cells_SS_only.to_excel (reduced_active_cells_file_Name)


           