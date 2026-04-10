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
                  '251', '252', '253', 
# eNB with funny names 
                  '123', '134', '185', '241', '406', '407', '409', '413', '414','415','417', '420','426', '999' )

readAudit = pd.read_csv(mmWaveAuditFile)

mmWList =  set (readAudit ['gNB_number'])

readAudit = pd.read_csv(cmWaveAuditFile)
cmWList = set (readAudit ['gNB_number'])


def NokiaOrSamsung (gnb):
    testValue = int(gnb)
    
    if (testValue  in mmWList ) :
       return "Nokia"
    elif (testValue in cmWList) :
       return "Nokia"
    else :
       return "Samsung" 

result = pd.DataFrame ()

def extractnbrGnbID (identifier):
    return int(identifier/16384)
    
    

def extractFreqType (gNB):
    
    if gNB%10000 > 9000:
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
               
for chunk in pd.read_csv(RAVS_Report, skiprows =5, usecols= ['Global eNodeB ID', 'Full Object Path', 'Value'],  chunksize = 50000):

  temp = chunk['Full Object Path'].str.split("/", expand = True )
  chunk ['lncel'] = temp[2].str.split ("-", expand = True) [1]
  chunk ['lnRelGnbCell']= temp[3].str.split ("-", expand = True ) [1]  
  chunk ['nbrGnbId']  = chunk['Value'].apply (extractnbrGnbID)
  chunk ['nbrCellId']  = chunk['Value']%16384
# =============================================================================
#   chunk ['freqType'] =  chunk['nbrGnbId'].apply( extractFreqType)    
#   chunk ['nbrCellIdHex'] =  chunk['nbrCellId'].apply(convertHEX)
#   chunk ['cband'] =  chunk['nbrCellIdHex'].apply(isCBAND)
# =============================================================================
  chunk ['marketId'] = chunk['Global eNodeB ID'].apply(extractMktId)  
  chunk ['vendor'] = chunk ['nbrGnbId'].apply(NokiaOrSamsung)
  result = pd.concat ([result , chunk], ignore_index=True)  

result.rename (columns = {"value" : "nrCellId"}, inplace=True ) 


print (result.info ())  

for mkt in VzMarketIdList :
    mktresult = result[result.marketId ==   mkt]
    mktresult.to_csv("eNB_per_" + mkt + ".csv")


print ('end conversion : ', pd.Timestamp.now ())
result.to_csv("largeFGN.csv")
print ('end write : ', pd.Timestamp.now ())
