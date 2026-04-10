

import os 
import shutil
# from shutil import unpack_archive

import configparser 

samsungConfig =  configparser.ConfigParser()

samsungConfig.read ('samsungConfig.ini')

with open('samsungConfig.ini', 'w') as samsungFile:
    samsungConfig.write(samsungFile)
rawData = samsungConfig ['dir']['rawData'] 
market_reports = samsungConfig ['dir']['market_reports']
nationwide_reports =  samsungConfig ['dir']['nationwide_reports']

file_name_elements = rawData.split('/')
file_name_elements.reverse()
current_date = file_name_elements [1]

dest = market_reports + current_date + '_Result_permarket.xlsx'

shutil.copy(rawData + 'sectorResult_permarket.xlsx', dest)

print ('copy : ', rawData + 'sectorResult_permarket.xlsx',' to : ',  dest)

dest = nationwide_reports  + current_date + '_nationwide_cells.xlsx'

shutil.copy(rawData + 'nationwide_cells.xlsx', dest)

print ('copy : ', rawData + 'nationwide_cells.xlsx',' to : ',  dest)
