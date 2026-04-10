
import shutil
import os 
import gzip
# from shutil import unpack_archive

import configparser 

samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')


rawData = samsungConfig ['dir']['rawData'] 
parse_date = rawData.split ('/')
# second to last entry is the actual date 
current_date = parse_date [ len (parse_date) - 2 ]
                                            
print ('current date ', current_date, )
new_raw_date = str (input ('enter new date or press enter to accept:'))
if not new_raw_date.strip (): 
   try: 
      base = samsungConfig ['dir']['base']
      os.chdir (base)
      full_path = base + '/' + new_raw_date.strip () +  '/' 
      os.mkdir (full_path)
      rawdate = full_path
      samsungConfig ['dir']['rawData']  = full_path
   except:
      print ('an error occured :', os.error ) 
os.chdir (rawData)
      

old_dir =  samsungConfig ['dir']['4week']

print ('enter directory with 4 week old (', old_dir, ') or press <enter to accept existing date:')
new_4week_date = str (input ())
if not new_raw_date.strip (): 
   try: 
      base = samsungConfig ['dir']['base']
      
      samsungConfig ['dir']['4week']  = new_4week_date   
   except :
       print ('an error occured :', os.error ) 

if new_4week_date or new_raw_date :
   with open('samsungConfig.ini', 'w') as samsungFile:
      samsungConfig.write(samsungFile)
    


#%% 
# This cell covers the case where the data is received as an e-mail attachment 
for datafile in os.scandir () :
    if (datafile.path.find ('gz.txt') > 0) :   
        oldname = datafile.path 
        newname = oldname.replace ('.gz.txt', '.gz')
        print ("renamed", oldname, " to ", newname)
        os.rename (oldname, newname)
        with gzip.open (newname, 'rb') as zippy:
            content = zippy.read()
            uncompressed_name = newname.replace ('.gz', '')
            print ("now decompressing to ", uncompressed_name)
            f = open (uncompressed_name, 'w+b')
            print (" success, content in memory")
            f.write (content)
            f.close()

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
       




 