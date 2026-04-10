#! /usr/bin/env python


import pandas as pd
import numpy as np
import seaborn as sns


# CSV files to parse


active_cells2_file_Name  = 'C:/Users/fn101139/Documents/SamsungSwap/02-06-2023/nationwide_cells_SS_Cband_cmw.xlsx'
active_cells1_file_Name  = 'C:/Users/fn101139/Documents/SamsungSwap/03-07-2023/nationwide_cells_SS_cBand_cmW.xlsx'
calculate_delta = True

nokia_colors = [(18/255, 65/255, 145/255), 
                # (0/255, 17/255, 53/255), (237/255, 242/255, 245/255),
                (190/255, 200/255, 210/255),(152/255, 162/255, 174/255), (77/255, 87/255, 102/255),
                (39/255, 49/255, 66/255), (0/255, 201/255, 255/255), (75/255, 221/255, 51/255)] 

markets_regions = 'C:/Users/fn101139/Documents/SamsungSwap/06-13-2022/sectorResult_permarket.xlsx'


market_result = pd.read_excel(markets_regions,   sheet_name = 'Sheet1')

if calculate_delta : 
  active_cells1 = pd.read_excel (active_cells1_file_Name, sheet_name = 'Sheet1')
  active_cells1 ['Nokia'] = active_cells1 ['Nokia'].astype ('boolean')
  print ('read 1 finish')

active_cells2 = pd.read_excel (active_cells2_file_Name, sheet_name = 'Sheet1')
active_cells2 ['Nokia'] = active_cells2['Nokia'].astype ('boolean')
print ('read 2 finish')

#%%
def delta_cells_in_df  (active_cells, remove_cells):
    '''Remove all rows from the dataframe active_cells, where the cell id 'nrCellId' matches a cell in the dataFrame remove_cells.  Returns a new DataFrame.'''  
    active_cell_set = set (active_cells ['nrCellId'])
    remove_cell_set = set (remove_cells ['nrCellId'])
    
    delta_cells_set = active_cell_set - remove_cell_set
    delta_cells_df = pd.DataFrame (delta_cells_set)
    delta_cells_df.columns  = ["cells"]
    active_cells.convert_dtypes(convert_integer = True)

    return delta_cells_df.merge (active_cells, how = 'left', left_on = 'cells', right_on = 'nrCellId')

if calculate_delta : 
    active_cells = delta_cells_in_df (active_cells2, active_cells1)
    print ('cells 1 : ', len (active_cells1), 'cells 2 : ', len (active_cells2), 'delta : ', (len (active_cells2) - len (active_cells1)) )
    print ('cband 1  : ', sum ((active_cells1 ['freqType'] == 'cBand')))
    print ('cband 2  : ', sum ((active_cells2 ['freqType'] == 'cBand')))
    print ('cmW (SS) 1 ', sum ((active_cells1 ['freqType'] == 'cmW') & (~active_cells1.Nokia)))
    print ('cmW (SS) 2 ', sum ((active_cells2 ['freqType'] == 'cmW') & (~active_cells2.Nokia)))

else :
    active_cells = active_cells2  
    
print ('dataframe shape active cells', active_cells.shape[0], active_cells.shape[1], active_cells.columns)

print ('cband added : ', sum ((active_cells ['freqType'] == 'cBand')))
print ('cmW (SS) added : ', sum ((active_cells ['freqType'] == 'cmW') & (~active_cells.Nokia)))
print ('cmW (Nokia) added : ', sum ((active_cells ['freqType'] == 'cmW') & (active_cells.Nokia)))
print ('mmW (SS) added : ', sum ((active_cells ['freqType'] == 'mmW') & (~active_cells.Nokia)))
print ('mmW (Nokia) added : ', sum ((active_cells ['freqType'] == 'mmW') & (active_cells.Nokia)))


# active_cells = active_cells1

VzMarketIdList = market_result['Market'].tolist()

regions =  market_result [ ['Market', 'Region']]

regions.set_index('Market')

#the following adds region to the frame based on the market ID
active_cells = active_cells.join(regions.set_index('Market'), on= 'marketId', how = 'left') 

active_cells.fillna( {'#gNB cBand Sectors' : 0, '#gNB cm Sectors' : 0 }, inplace = True )
active_cells ['total gNB size'] = active_cells ['#gNB cBand Sectors' ] + active_cells ['#gNB cm Sectors' ]

active_cells ['isCloud']  = active_cells ['total gNB size'] > 10
active_cells ['isBM']  = active_cells ['total gNB size'] < 5

active_cells ['isMultiFreq'] = np.where ( (active_cells ['freqType'] == 'cBand'), 
                                         (active_cells.isCloud & (active_cells ['#gNB cm Sectors' ] > 1)), 
                                          (active_cells.isCloud & (active_cells ['#gNB cBand Sectors'] > 1))) 

# print ('n2/n5 cells with cloud coverage, where the CU has no cBAND: ', active_cells.loc [ (active_cells.isCloud & (active_cells ['#gNB cBand Sectors'] < 5)) ] )

#%%
region_result = active_cells.groupby (['Region', 'freqType', 'Nokia', 'isBM']) ['nrCellId'].count()
region_df = region_result.to_frame().reset_index()
print ('results per region :')
print (region_df)

plot_me = region_df [region_df ['freqType'] == 'cmW']
ax1 = sns.barplot(y="Region", x="nrCellId", hue="isBM", data=plot_me, palette=nokia_colors)
columns = ax1.containers
ax1.bar_label (ax1.containers[0])
ax1.bar_label (ax1.containers[1])

# region_result = active_cells.groupby (['Region', 'freqType', 'isMultiFreq', 'isBM']) ['nrCellId'].count()
# region_df = region_result.to_frame().reset_index()

# plot_me =region_df.loc [(~region_df.isBM) & (region_df ['freqType'] == 'cBand'), ['Region', 'nrCellId', 'isMultiFreq']]
# ax2 = sns.barplot(y="Region", x="nrCellId", hue="isMultiFreq", data=plot_me, palette=nokia_colors)

# plot_me = region_df.loc [(~region_df.isBM) & (region_df ['freqType'] == 'cmW'), ['Region', 'nrCellId', 'isMultiFreq']]
# ax3 = sns.barplot(y="Region", x="nrCellId", hue="isMultiFreq", data=plot_me, palette=nokia_colors)


region_df.to_excel ('region_result.xlsx')



new_cell_cBand_cloud = sum ((active_cells ['freqType'] == 'cBand') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] > 10))

new_cell_cBand_bm  = sum ((active_cells ['freqType'] == 'cBand') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] < 5)) 

new_cell_cBand_unknown  = sum ((active_cells ['freqType'] == 'cBand') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] > 4) & 
                                    (active_cells [ 'total gNB size'] < 11) ) 



new_cell_cmW_cloud  = sum ((active_cells ['freqType'] == 'cmW') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] > 10 ))
new_cell_cmW_bm  = sum ((active_cells ['freqType'] == 'cmW') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] < 5 ))

new_cell_cmW_unknown  = sum ((active_cells ['freqType'] == 'cmW') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] > 4 )& 
                                    (active_cells [ 'total gNB size'] < 11 ))



print (" cBand cloud: ", new_cell_cBand_cloud)
print (" cBand BM: ", new_cell_cBand_bm)
print (" cBand unknown: ", new_cell_cBand_unknown)

print (" cmW cloud: ",  new_cell_cmW_cloud)
print (" cmW BM: ", new_cell_cmW_bm)
print (" cmW unknown: ", new_cell_cmW_unknown)

  
new_gNB_cmW_bm = active_cells.loc [(active_cells ['freqType'] == 'cmW') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] < 5), 'nbrGnbId'].unique ()

new_gNB_cmW_cloud = active_cells.loc [(active_cells ['freqType'] == 'cmW') & 
                                    (~ active_cells.Nokia) & 
                                    (active_cells [ 'total gNB size'] > 10), 'nbrGnbId'].unique ()



print ("new gNB:", new_gNB_cmW_bm, new_gNB_cmW_cloud)

