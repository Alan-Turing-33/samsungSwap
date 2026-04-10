

import os 
import gzip
# from shutil import unpack_archive



 
os.chdir ('C:/Users/fn101139/Documents/SamsungSwap/08-22-2022')

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
 
# for datafile in os.scandir () :
#     if (datafile.path.find ('.gztar') > 0) :   
#         newname = datafile.path 
#         unpack_archive(newname)


