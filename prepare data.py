
import shutil
import os 
import pathlib
import gzip
from datetime import date
# from shutil import unpack_archive

import configparser 

samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')


rawData = samsungConfig ['dir']['rawData'] 
parse_date = rawData.split ('/')
# second to last entry is the actual date 
current_date = parse_date [ len (parse_date) - 2 ]
base = samsungConfig ['dir']['base']
os.chdir (base)                                  
print ('current date ', current_date )
f = current_date.split('-') 
current_date_os_format = f[2] + '-' + f[0] + '-' + f[1] 
print ('converted date ', current_date_os_format)
print ('calculated current date ', date.today() )

transform = { '


#%% 
#

downloads = pathlib.Path (r'C:\Users\fn101139\Downloads')

 
for f in downloads.iterdir () :
	download_time = (f.stat().st_mtime)
#	print (f.name , ' created ', download_time)
	d = str (date.fromtimestamp (download_time))  	
	if current_date_os_format in d:
		print (f.name , "downloaded at :", d)
         		
    


try: 
   shutil.copy (old_dir + "sectorResult_permarket.xlsx", rawData + "sectorResult_permarket.xlsx")
except: 
  print ('could not copy sectorResult_permarket.xlsx')  

try: 
   shutil.copy (old_dir + "randy_4week_loss.xlsx", rawData + "randy_4week_loss.xlsx")
except: 
   print ('could not copy randy_4week_loss.xlsx')  

#%%
# this cell covers the case where the files are downloaded from RAVS via a web Link. In this case they are expected to have the format REPORT(<number>).CSV  
os.chdir ('C:/Users/fn101139/Downloads/')

for datafile in os.scandir () :
    if ((datafile.path.find ('report') == 2) & (datafile.path.find ('.csv') > 0)) : 
       print ('processing : ', datafile.path) 
       current_file = datafile.path.split(".\\").pop() 
       print ('move ', datafile.path, ' to ', rawData + current_file )
       shutil.move (datafile.path, rawData + current_file)
    elif ((datafile.path.find ('gNB NR Cell Summary') == 2) & (datafile.path.find ('.csv') > 0)) : 
       print ('processing : ', datafile.path) 
       current_file = datafile.path.split(".\\").pop() 
       print ('move ', datafile.path, ' to ', rawData + 'gNB NR Cell Summary.csv')
       shutil.move (datafile.path, rawData + 'gNB NR Cell Summary.csv')
       




 