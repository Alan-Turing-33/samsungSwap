inFileName="out_VzW_NRRELGNBCEL_nrCellId_report_03162022_1.csv"
extractMkt="184"

cmWaveAuditFile="vzw_comm_clsgnb_audit-gnb-latest.csv"
mmWaveAuditFile="vzw_comm_gnb_audit-gnb-latest.csv"

# get list of mmW and cmW gNBs
gNBList={ "mmW":[], "cmW":[] }
for line in open(mmWaveAuditFile) : gNBList["mmW"].append(line.split(",")[3])
for line in open(cmWaveAuditFile) : gNBList["cmW"].append(line.split(",")[3])

inFile=open(inFileName,"r")

print(inFile.readline().strip() + ",Nokia?" ) #header row

for line in inFile :
    tmp=line.strip().split(",")
    if tmp[0][:3]==extractMkt : 
        if ( tmp[4] in gNBList[tmp[7]] ) : #calculated gNB_Id is in the mmW / cmW list
            tmp.append( "Nokia" )
        else:
            tmp.append( "SS" )
        print( ",".join(tmp) )