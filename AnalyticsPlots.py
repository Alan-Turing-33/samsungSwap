#! /usr/bin/env python


import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import configparser

samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')

weekly_raw_data = samsungConfig ['dir']['rawData'] 

resultFileName= weekly_raw_data + 'sectorResult_permarket.xlsx'

resultByMarket = pd.read_excel(resultFileName,  sheet_name = 'Sheet1')

regionData = resultByMarket.groupby(['Region']).sum()
regionData.reset_index (inplace = True) 
regionData['c-band skip cell ratio'] = regionData ['NR rel CBand'] / regionData ['5G cell CBand'] * 1000
regionData ['loss sub 6 sector'] = regionData['loss gNB']  * 3.37 
regionData['loss delta sector'] = (regionData['loss eNB'] - regionData['loss gNB']) * 3.37

temp = regionData.set_index ('Region')
regions = regionData ['Region'].tolist() 
    
start_a = [ n for n in range (len (regions))   ]
start_b = [ x + 0.2 for x in start_a]
start_c = [ x + 0.2 for x in start_b]
plt.title ( " freq band distribution")
plt.barh(start_a, regionData ['5G cell cm Samsung'], height= 0.2)
plt.barh(start_a, regionData ['5G cell cm Nokia'], left = regionData ['5G cell cm Samsung'], height= 0.2)
plt.barh(start_b, regionData ['5G cell CBand'], height= 0.2)
plt.barh(start_c, regionData ['loss sub 6 sector'], height= 0.2)
plt.barh(start_c, regionData ['loss delta sector'], left = regionData ['loss sub 6 sector'], height= 0.2)

plt.legend(['FDD cell Samsung', 'FDD cell Nokia', 'CBand cell', 'loss sub-6 & LTE', 'loss LTE only'])
plt.yticks ([ x + 0.20 for x in start_a], regions)       
plt.show()
 
# # need to overwrite the agregated result with the average per region 
regionData ['5G cell C-band cm ratio']= regionData ['5G cell CBand'] / regionData ['5G cell cm']
sns.barplot(y="Region", x="5G cell C-band cm ratio", data = regionData, orient = 'h').set_title (' Cband cell per cm Cell for each region')
plt.show()


regionData ['n77 skip cell ratio']= regionData ['NR rel CBand'] / regionData ['5G cell CBand']  
    
sns.barplot(y="Region", x='n77 skip cell ratio', data = regionData, orient = 'h').set_title (' n77 skip cell ratio')
plt.show()

regionData ['n77 per LTE sector ratio']=  regionData ['5G cell CBand']/ (regionData [ 'Karl eNB '] * 3.37) 

print (regionData.loc [:, ['Region', 'n77 per LTE sector ratio']])


 