#! /usr/bin/env python


import pandas as pd 
import numpy as np
import os
import configparser

samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')

base_dir = samsungConfig ['dir']['base'] 

historic_region_data = pd.DataFrame(columns = ['Central Texas', 'Houston/Gulf Coast', 'New York Metro', 'Ohio',
       'Philadelphia Tri-State', 'South Central', 'Southern Virginia',
       'Washington/Baltimore', 'West Pennsylvania','Date'])
seaborn_data = pd.DataFrame(columns = ['Date', 'Region' , 'c-band skip cell ratio'])

os.chdir (base_dir)

for data_dir in os.scandir () :
    if ((data_dir.is_dir())) : 
       
      
       current_date = data_dir.path.split(".\\").pop() 
       if ('-202' in current_date): 
           all_column = False 
           result_id= data_dir.path + '\\sectorResult_permarket.xlsx'
           
           try :
             result_by_market = pd.read_excel(result_id,  sheet_name = 'Sheet1', usecols= 
                                          ['Region', '5G cell CBand', '5G cell CBand wo border', 'NR rel CBand' ])
             all_column = True
           
           except : 
               result_by_market = pd.read_excel(result_id,  sheet_name = 'Sheet1', usecols= 
                                              ['Region', '5G cell CBand', 'NR rel CBand' ])
                   
           finally : 
               print ('processing : ', data_dir.path + '\\sectorResult_permarket.xlsx') 
           if ('5G cell CBand wo border' in result_by_market.columns) :
               result_by_market ['5G cell CBand'] = np.where ((result_by_market['5G cell CBand wo border'] > 0), 
                                                          result_by_market['5G cell CBand wo border'], result_by_market ['5G cell CBand'])
               result_by_market.drop(columns = '5G cell CBand wo border', inplace = True)
           region_data = result_by_market.groupby(['Region']).sum()
           region_data['c-band skip cell ratio'] = region_data ['NR rel CBand'] / region_data ['5G cell CBand']
           skip_cell_per_region = region_data.transpose (copy= True)
           skip_cell_per_region.columns = list (region_data.index) 
           skip_cell_per_region.drop (axis = 0, index = ['NR rel CBand', '5G cell CBand'], inplace  = True)
           skip_cell_per_region ['Date'] = current_date
                       
           historic_region_data = pd.concat ([historic_region_data, skip_cell_per_region])
           
           region_data ['Region'] = region_data.index
           region_data ['Date']   = current_date 
           seaborn_data = pd.concat ([seaborn_data, region_data])

historic_region_data.index = historic_region_data ['Date']

historic_region_data.to_excel ('historic_region_data.xlsx')

#%%

import seaborn as sns 

seaborn_data.index = range (seaborn_data.shape [0]) 
seaborn_data ['Date'] = pd.to_datetime (seaborn_data ['Date'])
seaborn_data ['week'] = seaborn_data ['Date'].dt.isocalendar().week
# seaborn_data.drop ( ['NR rel CBand', '5G cell CBand'], axis = 1, inplace  = True)
# sns.lineplot (data = seaborn_data)

# sns.lineplot (data = historic_region_data)

sns.set(rc={"figure.figsize":(16, 8)})
sns.lineplot(data = seaborn_data, x = 'Date', y = 'c-band skip cell ratio', hue = 'Region')
# plot1.set_xticklables (plot1.get_xticklables (), rotation = 50), 

    
# start_a = [ n for n in range (len (regions))   ]
# start_b = [ x + 0.2 for x in start_a]
# start_c = [ x + 0.2 for x in start_b]
# plt.title ( " freq band distribution")
# plt.barh(start_a, region_data ['5G cell cm Samsung'], height= 0.2)
# plt.barh(start_a, region_data ['5G cell cm Nokia'], left = region_data ['5G cell cm Samsung'], height= 0.2)
# plt.barh(start_b, region_data ['5G cell CBand'], height= 0.2)
# plt.barh(start_c, region_data ['loss sub 6 sector'], height= 0.2)
# plt.barh(start_c, region_data ['loss delta sector'], left = region_data ['loss sub 6 sector'], height= 0.2)

# plt.legend(['FDD cell Samsung', 'FDD cell Nokia', 'CBand cell', 'loss sub-6 & LTE', 'loss LTE only'])
# plt.yticks ([ x + 0.20 for x in start_a], regions)       
# plt.show()
 
# # # need to overwrite the agregated result with the average per region 
# region_data ['5G cell C-band cm ratio']= region_data ['5G cell CBand'] / region_data ['5G cell cm']
# sns.barplot(y="Region", x="5G cell C-band cm ratio", data = regionData, orient = 'h').set_title (' Cband cell per cm Cell for each region')
# plt.show()


# region_data ['n77 skip cell ratio']= region_data ['NR rel CBand'] / region_data ['5G cell CBand']  
    
# sns.barplot(y="Region", x='n77 skip cell ratio', data = regionData, orient = 'h').set_title (' n77 skip cell ratio')
# plt.show()

# region_data ['n77 per LTE sector ratio']=  region_data ['5G cell CBand']/ (region_data [ 'Karl eNB '] * 3.37) 

# print (region_data.loc [:, ['Region', 'n77 per LTE sector ratio']])


 