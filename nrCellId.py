#! /usr/bin/env python

# CSV files to parse
#inputFiles=[ "VZW_LNRELGNBCELL_NRCELLID_1.1.csv", "VZW_LNRELGNBCELL_NRCELLID_1.2.csv", "VZW_LNRELGNBCELL_NRCELLID_1.3.csv", "VZW_LNRELGNBCELL_NRCELLID_1.4.csv" ]
inputFiles=["VzW_NRRELGNBCEL_nrCellId_report_03162022.csv"]

# Coloumns of interest and indices
# C: Global eNodeB ID - 2
# I: Full Object Path - 8 --> get LNCEL and LNRELGNBCELL value
# K: Value - 10

# lines to ignore - included header row
ignoreLines = 6

for inFile in inputFiles :
    linesRead = 0
    outFile = open( "out_"+inFile, "w" )
    outFile.write("Global eNodeB ID,LNCEL,LNRELGNBCELL,nrCellId,calcNbrGnbId,calcNbrCellId,calcNbrCellIdHex,mmW/cmW,CBand?\n" )
    for line in open( inFile, "r" ) :
        if linesRead < ignoreLines: linesRead += 1 # ignore initial lines
        else:
#            line.replace("Philadelphia,", "Philadelphia")
 #           line.replace("Memphis,", "Memphis")
            tmp=[ x.strip('"') for x in line.split('","') ]
            # get lncel and nbr obj ids from MRBTS-107001/LNBTS-107001/LNCEL-12/LNRELGNBCELL-0
            try:
                objPath= tmp[8].split("/") 
                lncel=objPath[2].split("-")[1]
                lnRelGnbCell = objPath[3].split("-")[1]
                nrCellId=int(tmp[10])
            except IndexError : 
                print( tmp )
                continue
            nbrGnbId=int(nrCellId/16384)
            nbrCellId=nrCellId%16384
            freqType = "cmW" if nbrGnbId%10000 > 9000 else "mmW"
            nbrCellIdHex = str(hex(nbrCellId))
            cband = ( nbrCellIdHex[-1:] == "a" )
            #outFile.write( ",".join( [ tmp[2], lncel, lnRelGnbCell, tmp[10] ] ) + "\n" )
            outFile.write( ",".join( [ tmp[2], lncel, lnRelGnbCell, tmp[10], str(nbrGnbId), str(nbrCellId), nbrCellIdHex, freqType, str(cband) ] ) + "\n" )
    

