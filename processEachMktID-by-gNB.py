#! /usr/bin/env python


import pandas as pd

print ('start conversion : ', pd.Timestamp.now ())
# CSV files to parse

cmWaveAuditFile="vzw_comm_clsgnb_audit-gnb-latest.csv"
mmWaveAuditFile="vzw_comm_gnb_audit-gnb-latest.csv"

# Coloumns of interest and indices
# C: Global eNodeB ID - 2
# I: Full Object Path - 8 --> get LNCEL and LNRELGNBCELL value
# K: Value - 10

# # =============================================================================
# VzMarketIdList = ('78', '79', '80','81', '82', '84', '85', '86', '87', '88', 
#                   '89', '90', '91', '96', '97', '98', '99', '100', '101', '102', 
#                   '106', '107', '109', '110', '111', '112', '113', '114', '115',
#                   '117', '120', '121', '122', '125', '126', '127', '131', '132', 
#                   '133', '135', '136', '137', '138', '139', '140', '181', '182', 
#                   '184', '186', '242', '243', '244', '245', '246', '247', '250', 
#                   '251', '252', '253', 
# # eNB with funny names 
#                   '123', '134', '185', '241', '406', '407', '409', '413', '414','415','417', '420','426', '999' )


VzMarketIdList = ( '555', '78' )

readAudit = pd.read_csv(mmWaveAuditFile)

mmWList =  set (readAudit ['gNB_number'])

readAudit = pd.read_csv(cmWaveAuditFile)
cmWList = set (readAudit ['gNB_number'])


def NokiaOrSamsung (gnb):
    testValue = int(gnb)
    
    if (testValue  in mmWList ) :
       return "mmNokia"
    elif (testValue in cmWList) :
       return "cmNokia"
    else :
       return "Samsung" 

    

def extractFreqType (gNB):
# uses the 4 digit from the right to check for vRAN 1.0 or other. assumption vRAN 1.0  = 0 , cmwave and       
   if (type(gNB) != int) :
      print (type (gNB))
    
   if gNB%10000 > 9000:
     value = "cmW" 
   else :
      value = "mmW"
   return value      

def convertHEX (identifier):
    return str(hex(identifier)) 
               
def isCBAND (identifier):
   return identifier [-1:] == "a"


#def extractFreqType (cellID) 
# use the last   
#    if (type(gNB) != int) :
#        print (type (gNB))
    
#     if gNB%10000 > 9000:
#       value = "cmW" 
#     else :
#       value = "mmW"
#     return value      
resultByMarket =  pd.DataFrame({'market' : [ ], 
                       'numeNB' : [], 
                       'numSector' :[],
                       'NgbgNB' :[],
                       'SectorWithCm' : [],
                       'SectorWithMm' : [],
                       'SectorWithCBand' : [], 
                       'SectorWithCmNokia' : [], 
                       'SectorWithmmNokia' : [],
                       'SectorWithSamsung' : [],
                       'SectorWithExclusiceCm' : [],
                       'SectorWithExclusiveMm' : [],
                       'SectorWithExclusiveCBand' : [],
                       'SectorNokiaExclusive ' : [], 
                       'SectorSamsungExclusive' : [],
                       'SectorWithCBand0' : [],
                       'SectorWithCBand1' : [], 
                       'SectorWithCBand2' : [],
                       'SectorWithCBand3' : []
                       })


def analyticsPerMarket (marketId):
    
    print ('start analysis for ',   marketId)
    print ('start time : ', pd.Timestamp.now ())
               
    MktData = pd.read_csv("C:/Users/fn101139/Documents/SamsungSwap/eNB_per_" + marketId + ".csv")


    resultByeNB = pd.DataFrame({'gNB' : [ ], 
                       'Totalsectors' : [], 
                       'cmWaveSectors' :[],
                       'mmWaveSectors' :[],
                       'cBandSectors' : [],
                       'cmnokia' : [],
                       'mmnokia' : [], 
                       'samsung' : []})
     
    MktData ['freqType'] =  MktData['nbrGnbId'].apply( extractFreqType)    

#    MktData ['nbrCellIdHex'] =  MktData['nbrCellId'].apply(convertHEX)
#    MktData ['cBand'] =  MktData['nbrCellIdHex'].apply(isCBAND)
# MktData ['freqType'] = 'cBand'.all() if (MktData ['cBand']) else  MktData ['freqType']
 
    MktData['vendor'] = MktData ['nbrGnbId'].apply(NokiaOrSamsung)
    MktData['uniqueSector'] = (MktData ['Global eNodeB ID'] * 100) + (MktData ['lncel'] // 10)
   
    for index, data  in MktData.iterrows():
#        MktData.at [index, 'uniqueSector'] = MktData [index, 'Global eNodeB ID'] * 100 + int (MktData [index, 'lncel']/10)  
      current_nbr = MktData.loc[index, 'nbrCellId']
     
      
      if isCBAND(convertHEX(current_nbr)) == True :
         MktData.at [index, 'freqType' ] = 'cBand'
         if MktData.at [index, 'vendor']  == 'mmNokia' :
           MktData.at [index, 'vendor'] = 'cBandNokiamm'
         if MktData.at [index, 'vendor']  == 'cmNokia' :
           MktData.at [index, 'vendor'] = 'cBandNokiacm'
         
    
      
    numeNBinMarket = MktData ['Global eNodeB ID'].nunique()
    NumeNBsectors = MktData['uniqueSector'].nunique()
    NumNeighbourgNB = MktData['nbrGnbId'].nunique()
    
    
    
    for currentgNB in pd.unique (MktData['nbrGnbId']):
         gNBData = MktData [MktData ['nbrGnbId'] == currentgNB]
         numgNB =   pd.unique (sectorData ['nbrGnbId']).size
         numgNB1 = sectorData ['nbrGnbId'].nunique() 
        
         if numgNB != numgNB1 : 
             print ('numgNB and numgNB1  diff', numgNB, '  ' , numgNB1)
         
         temp = sectorData[sectorData ['freqType'] == 'cmW']
         cmWave =   pd.unique (temp ['nbrGnbId']).size
         temp = sectorData[sectorData ['freqType'] == 'mmW']
         mmWave =  pd.unique (temp ['nbrGnbId']).size
         temp = sectorData[sectorData ['freqType'] == 'cBand']
         cBand =  pd.unique (temp ['nbrGnbId']).size
         temp = sectorData[sectorData ['vendor'] == 'cmNokia']
         cmnokia =  pd.unique (temp ['nbrGnbId']).size
         temp = sectorData[sectorData ['vendor'] == 'mmNokia']
         mmnokia =  pd.unique (temp ['nbrGnbId']).size
         temp = sectorData[sectorData ['vendor'] == 'Samsung']
         samsung =  pd.unique (temp ['nbrGnbId']).size                   
         resultBySector.loc[len(resultBySector.index)] = [sector, numgNB, cmWave, mmWave, cBand, cmnokia, mmnokia, samsung]
         allcmWavefilter = (resultBySector ['cmWave'] > 0)
         
    allcmWavefilter = (resultBySector ['cmWave'] > 0)
    allcmWave = resultBySector.loc [allcmWavefilter].shape[0]
#    print (' number of sectors with cm wave connections', allcmWave)   

# calcREsult = [ 'NumgNB ', 'sectors', 'NgNB' 'cmWaveSec', 'cmWaveNokia', 'mmWave', 'mmWaveNokia',  'cBand', ]        
    
    allmmWavefilter = resultBySector ['mmWave'] > 0
    allmmWave = resultBySector [allmmWavefilter].shape[0]
#    print (' number of sectors with mm wave connections', allmmWave) 
    
    allcBandfilter = resultBySector ['cBand'] > 0
    allcBand = resultBySector [allcBandfilter].shape[0]
#    print (' number of sectors with cBand wave connections', allcBand) 
    
    allNokiafilter = resultBySector ['cmnokia'] > 0
    allNokiacm = resultBySector [allNokiafilter].shape[0]
    
    allNokiafilter = resultBySector ['mmnokia'] > 0
    allNokiamm = resultBySector [allNokiafilter].shape[0]
    resultBySector
    allSamsungfilter = resultBySector ['samsung'] > 0
    allSamsung = resultBySector [allSamsungfilter].shape[0]
#    print (' number of sectors with Samsung connections', allSamsung) 
    
    
    #---------------------------------------------
    # exclusive 
    allcmWavefilter = (resultBySector ['cmWave'] > 0) & (resultBySector ['mmWave'] == 0) & (resultBySector ['cBand'] == 0)
    allcmWaveExclusive = resultBySector [allcmWavefilter].shape[0]
#    print (' number of sectors with exclusive cm wave connections', allcmWave)   
#    print (' sum usage : number of sectors with exclusive cm wave connections', sum (allcmWavefilter))  
    allmmWavefilter = (resultBySector ['cmWave'] == 0) & (resultBySector ['mmWave'] > 0) & (resultBySector ['cBand'] == 0)
    allmmWaveExclusive = resultBySector [allmmWavefilter].shape[0]
#    print (' number of sectors with exclusive mm wave connections', allmmWave) 
    
    allcBandfilter = (resultBySector ['cmWave'] == 0) & (resultBySector ['mmWave'] == 0) & (resultBySector ['cBand'] > 0)
    allcBandExclusive = resultBySector [allcBandfilter].shape[0]
#    print (' number of sectors with exclusive cBand wave connections', allcBand) 
    
    allNokiafilter =   (resultBySector ['samsung'] == 0) 
    allNokiaExclusive = sum( allNokiafilter)
#    print (' Nokia exclusive connections', allNokia) 
    
    allSamsungfilter =  (resultBySector ['cmnokia'] == 0) & (resultBySector ['mmnokia'] == 0 )
    allSamsungExclusive = sum (allSamsungfilter)
#    print (' Samsung exclusive connections', allSamsung) 
    
    
    
    allcBandfilter = (resultBySector ['cBand'] == 0) 
    allcBand0 = resultBySector [allcBandfilter].shape[0]
#    print (' cband overlay  0', allcBand)
    
    allcBandfilter = (resultBySector ['cBand'] == 1) 
    allcBand1 = resultBySector [allcBandfilter].shape[0]
 #   print (' cband overlay  1', allcBand)
    
    allcBandfilter = (resultBySector ['cBand'] == 2) 
    allcBand2 = resultBySector [allcBandfilter].shape[0]
 #   print (' cband overlay  2', allcBand)
    allcBandfilter = (resultBySector ['cBand'] == 3) 
    allcBand3 = resultBySector [allcBandfilter].shape[0]
 #   print (' cband overlay  3', allcBand)
    
    resultByMarket.loc[len(resultByMarket.index)] = [marketId , 
                                                     numeNBinMarket, 
                                                     NumeNBsectors, 
                                                     NumNeighbourgNB, 
                                                     allcmWave, 
                                                     allmmWave, 
                                                     allcBand, 
                                                     allNokiacm, 
                                                     allNokiamm , 
                                                     allSamsung, 
                                                     allcmWaveExclusive, 
                                                     allmmWaveExclusive, 
                                                     allcBandExclusive, 
                                                     allNokiaExclusive,
                                                     allSamsungExclusive,
                                                     allcBand0,
                                                     allcBand1,
                                                     allcBand2,
                                                     allcBand3]
       
       
    MktData.to_csv("C:/Users/fn101139/Documents/SamsungSwap/eNB_per_" + marketId + "_calc.csv")
    resultBySector.to_csv ("C:/Users/fn101139/Documents/SamsungSwap/eNB_per_" + marketId + "_sector.csv")
    
    print ('end conversion for',  marketId ,  " : " , pd.Timestamp.now ())
        
 # end of main function        
        
for mkt in  VzMarketIdList:
    analyticsPerMarket (mkt)       


resultByMarket.to_csv ("C:/Users/fn101139/Documents/SamsungSwap/sectorResult_permarket.csv")
           