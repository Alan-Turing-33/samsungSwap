#! /usr/bin/env python


import pandas as pd

print ('start conversion : ', pd.Timestamp.now ())
# CSV files to parse

RAVS_Report="VzW_NRRELGNBCEL_nrCellId_report_03162022.csv"
cmWaveAuditFile="vzw_comm_clsgnb_audit-gnb-latest.csv"
mmWaveAuditFile="vzw_comm_gnb_audit-gnb-latest.csv"

# Coloumns of interest and indices
# C: Global eNodeB ID - 2
# I: Full Object Path - 8 --> get LNCEL and LNRELGNBCELL value
# K: Value - 10

VzMarketIdList = ('78', '79', '80','81', '82', '84', '85', '86', '87', '88', 
                  '89', '90', '91', '96', '97', '98', '99', '100', '101', '102', 
                  '106', '107', '109', '110', '111', '112', '113', '114', '115',
                  '117', '120', '121', '122', '125', '126', '127', '131', '132', 
                  '133', '135', '136', '137', '138', '139', '140', '181', '182', 
                  '184', '186', '242', '243', '244', '245', '246', '247', '250', 
                  '251', '252', '253' )

readAudit = pd.read_csv(mmWaveAuditFile)

mmWList =  set (readAudit ['gNB_number'])

readAudit = pd.read_csv(cmWaveAuditFile)
cmWList = set (readAudit ['gNB_number'])


def NokiaOrSamsung (gnb):
    testValue = int(gnb)
    
    if (testValue  in mmWList ) :
       return "Nokia mmWave"
    elif (testValue  in cmWList) :
       return "Nokia cmWave"
    else :
       return "Samsung" 

print (NokiaOrSamsung ('999811'))         

result = pd.DataFrame ()

def extractFreqType (identifier):
    if identifier%10000 > 9000:
      value = "cmW" 
    else :
      value = "mmW"
    return value      

def convertHEX (identifier):
    return str(hex(identifier)) 
               
def isCBAND (identifier):
   return identifier [-1:] == "a"

def extractMktId (identifier):
    IdAsString = str(identifier)
    for mkt in VzMarketIdList :
       if IdAsString.startswith (mkt):
           return mkt
    return '999'   
