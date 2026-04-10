#! /usr/bin/env python


import pandas as pd


# CSV files to parse

all_active_cells_file_Name  = 'C:/Users/fn101139/Documents/SamsungSwap/08-015-2022/nationwide_cells.xlsx'

active_cells = pd.read_excel (all_active_cells_file_Name, sheet_name = 'Sheet1')
print ('read 1 finish')

cells_SS_only = active_cells [~active_cells.Nokia & (active_cells.freqType != 'mmW')]

filename_components = all_active_cells_file_Name.split(".")
reduced_active_cells_file_Name = filename_components [0] + '_SS_cBand_cmW.' + filename_components [1]

cells_SS_only.to_excel (reduced_active_cells_file_Name)