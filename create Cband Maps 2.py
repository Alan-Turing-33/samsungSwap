# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 14:51:25 2022

@author: fn101139
"""

import pandas as pd  
import numpy as np
import folium 

all_eNB_location = pd.read_csv('C:/Users/fn101139/Documents/SamsungSwap/eNB_location/all_eNB.csv', on_bad_lines = 'skip')
print ('locations loaded : ', all_eNB_location.shape [0])

all_eNB_location ['marketId'] = np.where ((all_eNB_location['Global eNodeB ID'] // 1000) < 300, (all_eNB_location['Global eNodeB ID'] // 1000), (all_eNB_location['Global eNodeB ID'] // 1000) - 300)


def map_cBand (market_id) :

   my_market = pd.read_csv ("C:/Users/fn101139/Documents/SamsungSwap/12-05-2022/cells_per_eNB" + str (market_id) + ".csv", on_bad_lines = 'skip')
   print (str (market_id) , ' : c-band cell info loaded : ', my_market.shape [0])
   cBand_info = my_market.loc [my_market['freqType']== 'cBand', ['Global eNodeB ID', 'nbrCellId']]
   
   market_locations =   all_eNB_location.loc [((all_eNB_location['marketId'] == market_id) & (all_eNB_location['BBU Latitude Coordinates'] != 'unset' ))  , ['Global eNodeB ID','BBU Latitude Coordinates', 'BBU Longitude Coordinates']]
  
   market_locations = market_locations.astype ({ 'BBU Latitude Coordinates' : float , 'BBU Longitude Coordinates' : float} , copy = False )
   print (market_locations ['BBU Latitude Coordinates' ].max())
   print (market_locations ['BBU Longitude Coordinates' ].min())
   # avg_long = market_locations ['BBU Longitude Coordinates'].sum() 
   # valid_entries = len (market_locations [market_locations['BBU Longitude Coordinates'] != 0 ]) 
   # print ('sum :', type (avg_long), "  ", avg_long)
   # print ('valid:', type (valid_entries ), '  ', valid_entries )
   # avg_long = avg_long / valid_entries
   # avg_lat = market_locations ['BBU Latitude Coordinates'].sum() 
   # valid_entries = len (market_locations [market_locations['BBU Latitude Coordinates'] != 0 ]) 
   # avg_lat = avg_lat / valid_entries  
   try :
     m = folium.Map(location= [  market_locations ['BBU Latitude Coordinates' ].max(), market_locations ['BBU Longitude Coordinates' ].min()], zoom_start=10)
   except :
       print ('cant create map at ',  market_locations ['BBU Longitude Coordinates' ].min(), market_locations ['BBU Latitude Coordinates' ].max())
       return 
   marker_added = 0 
   marker_failed = 0  

   for eNB  in my_market ['Global eNodeB ID'] :

        lookup_Lat =  all_eNB_location.loc [all_eNB_location['Global eNodeB ID'] == eNB, ['BBU Latitude Coordinates']]
        lookup_Long = all_eNB_location.loc [all_eNB_location['Global eNodeB ID'] == eNB, ['BBU Longitude Coordinates']]
        if (lookup_Lat.shape [0] > 0) & (lookup_Long.shape [0] > 0) :
          current_Lat = lookup_Lat.iat [0,0]
          current_Long = lookup_Long.iat [0,0]
          if  (eNB in set (cBand_info ['Global eNodeB ID']) ) :
              try :
                  cBand_count = int (cBand_info.loc  [cBand_info ['Global eNodeB ID'] ==  eNB, 'nbrCellId']) 
              except :
                  print ("error " ,  eNB)
                  
          else : 
              cBand_count = 0     
    
          if  (cBand_count > 100) :
             valcolor = 'darkred'  
          elif  cBand_count > 80 :
             valcolor = 'purple'
          elif  cBand_count > 60 :
             valcolor = 'lightred'
          elif  cBand_count > 40 :
             valcolor = 'pink'
          elif cBand_count > 20 :
             valcolor = 'green'
          elif  cBand_count > 0 :
             valcolor = 'blue'
          else :
             valcolor = 'lightgray'
          detail = "<i>" + str (eNB) + " cBand cells : " +  str (cBand_count) + "</i>"
          try :                           
            folium.Marker( [current_Lat, current_Long ], icon=folium.Icon (color = valcolor, icon = ''),  popup=detail).add_to(m)
            marker_added = marker_added + 1  
          except:  
             marker_failed = marker_failed + 1  
   print ('marker added : ', marker_added)
   print ('marker failed : ', marker_failed)

   m.save ('C:/Users/fn101139/Documents/SamsungSwap/maps/cBand_map_' + str (market_id) + '.html')


for market in [  78, 79, 
                80, 81, 82, 84, 85, 86, 87, 88, 89, 90, 91, 96, 97, 98, 99,
                100, 101, 102, 106, 107,109, 110, 111, 112, 113, 114, 115,  117, 
                120, 121, 122, 123, 124, 125, 126, 127, 131, 132, 133, 134, 135, 136, 
                137, 138, 139, 140, 181, 182, 184, 185, 186, 241, 242, 243, 244, 245, 
                246, 247, 250, 251, 252, 253, 254, 255 ]: 
     map_cBand(market)  