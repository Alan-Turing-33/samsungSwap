#! /usr/bin/env python


import pandas as pd
import cloudAdded



markets_regions = 'C:/Users/fn101139/Documents/SamsungSwap/06-13-2022/sectorResult_permarket.xlsx'


market_result = pd.read_excel(markets_regions,   sheet_name = 'Sheet1')
VzMarketIdList = market_result['Market'].tolist()

regions =  market_result [ ['Market', 'Region']]

regions.set_index('Market')


def extract_cells_mktId (file_name):
#     active_cells = pd.read_excel (file_name, usecols= ['nrCellId', 'marketId', 'freqType', 'Nokia'],  sheet_name = 'Sheet1')
    active_cells = pd.read_excel (file_name,  sheet_name = 'Sheet1')
    active_cells = active_cells.join(regions.set_index('Market'), on= 'marketId', how = 'left') 

    active_cells.fillna( {'#gNB cBand Sectors' : 0, '#gNB cm Sectors' : 0 }, inplace = True )
    active_cells ['total gNB size'] = active_cells ['#gNB cBand Sectors' ] + active_cells ['#gNB cm Sectors' ]

    active_cells ['isCloud']  = active_cells ['total gNB size'] > 10
    active_cells ['isBM']  = active_cells ['total gNB size'] < 5
    
    return active_cells 
    

active_cells_05_14 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/05-16-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_05_23 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/05-23-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_05_31 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/05-31-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_06_07 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/06-07-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_06_13 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/06-13-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_06_20 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/06-20-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_06_27 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/06-27-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_07_04 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/07-04-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_07_11 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/07-11-2022/nationwide_cells_SS_cBand_cmW.xlsx')
active_cells_07_18 = extract_cells_mktId ('C:/Users/fn101139/Documents/SamsungSwap/07-18-2022/nationwide_cells_SS_cBand_cmW.xlsx')

#%%


delta1 = cloudAdded.delta_cells_in_df(active_cells_05_14, active_cells_05_23)
delta2 = cloudAdded.delta_cells_in_df(active_cells_05_23, active_cells_05_31)
delta3 = cloudAdded.delta_cells_in_df(active_cells_05_31, active_cells_06_07)
delta4 = cloudAdded.delta_cells_in_df(active_cells_06_07, active_cells_06_13)
delta5 = cloudAdded.delta_cells_in_df(active_cells_06_13, active_cells_06_20)
delta6 = cloudAdded.delta_cells_in_df(active_cells_06_20, active_cells_06_27)
delta7 = cloudAdded.delta_cells_in_df(active_cells_06_27, active_cells_07_04)
delta8 = cloudAdded.delta_cells_in_df(active_cells_07_04, active_cells_07_11)
delta9 = cloudAdded.delta_cells_in_df(active_cells_07_11, active_cells_07_18)


delta1_cell = set ((delta1.loc [(delta1 ['freqType'] == 'cmW') & (~ delta1.Nokia),  'nrCellId']))

print ('delta 1 size ',  delta1.shape[0] )
  
print ('delta 1 found in 05-31', len (delta1_cell & set (active_cells_05_31 ['nrCellId']) ))
print ('delta 1 found in 06-07', len (delta1_cell & set (active_cells_06_07 ['nrCellId']) ))
print ('delta 1 found in 06-13', len (delta1_cell & set (active_cells_06_13 ['nrCellId']) ))
print ('delta 1 found in 06-20', len (delta1_cell & set (active_cells_06_20 ['nrCellId']) ))
print ('delta 1 found in 06-27', len (delta1_cell & set (active_cells_06_27 ['nrCellId']) ))
print ('delta 1 found in 07-04', len (delta1_cell & set (active_cells_07_04 ['nrCellId']) ))
print ('delta 1 found in 07-11', len (delta1_cell & set (active_cells_07_11 ['nrCellId']) ))
print ('delta 1 found in 07-18', len (delta1_cell & set (active_cells_07_18 ['nrCellId']) ))

delta1_cell = set ((delta2.loc [(delta2 ['freqType'] == 'cmW') & (~ delta2.Nokia),  'nrCellId']))

  
print ('delta 2 size ',  delta2.shape[0] )
print ('delta 2 found in 06-07', len (delta1_cell & set (active_cells_06_07 ['nrCellId'])) )
print ('delta 2 found in 06-13', len (delta1_cell & set (active_cells_06_13 ['nrCellId'])) )
print ('delta 2 found in 06-20', len (delta1_cell & set (active_cells_06_20 ['nrCellId'])) )
print ('delta 2 found in 06-27', len (delta1_cell & set (active_cells_06_27 ['nrCellId'])) )
print ('delta 2 found in 07-04', len (delta1_cell & set (active_cells_07_04 ['nrCellId'])) )
print ('delta 2 found in 07-11', len (delta1_cell & set (active_cells_07_11 ['nrCellId'])) )
print ('delta 2 found in 07-18', len (delta1_cell & set (active_cells_07_18 ['nrCellId'])) )


delta1_cell = set ((delta3.loc [(delta3 ['freqType'] == 'cmW') & (~ delta3.Nokia),  'nrCellId']))

print ('delta 3 size ',  delta3.shape[0] )  

print ('delta 3 found in 06-13', len (delta1_cell & set (active_cells_06_13 ['nrCellId'])) )
print ('delta 3 found in 06-20', len (delta1_cell & set (active_cells_06_20 ['nrCellId'])) )
print ('delta 3 found in 06-27', len (delta1_cell & set (active_cells_06_27 ['nrCellId'])) )
print ('delta 3 found in 07-04', len (delta1_cell & set (active_cells_07_04 ['nrCellId'])) )
print ('delta 3 found in 07-11', len (delta1_cell & set (active_cells_07_11 ['nrCellId'])) )
print ('delta 3 found in 07-18', len (delta1_cell & set (active_cells_07_18 ['nrCellId'])) )


delta1_cell = set ((delta4.loc [(delta4 ['freqType'] == 'cmW') & (~ delta4.Nokia),  'nrCellId']))

print ('delta 4 size ',  delta4.shape[0] )  
  
print ('delta 4 found in 06-20', len (delta1_cell & set (active_cells_06_20 ['nrCellId'])) )
print ('delta 4 found in 06-27', len (delta1_cell & set (active_cells_06_27 ['nrCellId'])) )
print ('delta 4 found in 07-04', len (delta1_cell & set (active_cells_07_04 ['nrCellId'])) )
print ('delta 4 found in 07-11', len (delta1_cell & set (active_cells_07_11 ['nrCellId'])) )
print ('delta 4 found in 07-18', len (delta1_cell & set (active_cells_07_18 ['nrCellId'])) )

delta1_cell = set ((delta5.loc [(delta5 ['freqType'] == 'cmW') & (~ delta5.Nokia),  'nrCellId']))

print ('delta 5 size ',  delta5.shape[0] )  
  
print ('delta 5 found in 06-27', len (delta1_cell & set (active_cells_06_27 ['nrCellId'])) )
print ('delta 5 found in 07-04', len (delta1_cell & set (active_cells_07_04 ['nrCellId'])) )
print ('delta 5 found in 07-11', len (delta1_cell & set (active_cells_07_11 ['nrCellId'])) )
print ('delta 5 found in 07-18', len (delta1_cell & set (active_cells_07_18 ['nrCellId'])) )

delta1_cell = set ((delta6.loc [(delta6 ['freqType'] == 'cmW') & (~ delta6.Nokia),  'nrCellId']))

print ('delta 6 size ',  delta6.shape[0] )  
  
print ('delta 6 found in 07-04', len (delta1_cell & set (active_cells_07_04 ['nrCellId'])) )
print ('delta 6 found in 07-11', len (delta1_cell & set (active_cells_07_11 ['nrCellId'])) )
print ('delta 6 found in 07-18', len (delta1_cell & set (active_cells_07_18 ['nrCellId'])) )

delta1_cell = set ((delta7.loc [(delta6 ['freqType'] == 'cmW') & (~ delta7.Nokia),  'nrCellId']))

print ('delta 6 size ',  delta6.shape[0] )  
  

print ('delta 7 found in 07-11', len (delta1_cell & set (active_cells_07_11 ['nrCellId'])) )
print ('delta 7 found in 07-18', len (delta1_cell & set (active_cells_07_18 ['nrCellId'])) )


#%% adding big picture 

big_delta = pd.concat ([delta1, delta2,delta3, delta4, delta5, delta6,delta7], join = 'inner') 
 

print (big_delta.shape [0])
