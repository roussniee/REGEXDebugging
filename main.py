####################
# Read Azure Results
####################
  
##################
# Import Packages
##################

from cmath import nan
from operator import index
import ocr_functions as ocr
import local_ocr_functions as locr
import highlighter
from unittest import result
from statistics import stdev
import os
import json
import pandas as pd
import re
import numpy as np
import warnings
import pyodbc
from credentials import epco_sql
warnings.filterwarnings("ignore")

## Connect to the SQL database
# connection_string = 'connection string here'
# conn = pyodbc.connect(connection_string)

# ## Pull abbreviations and names Table from SQL
# query = "SELECT fields FROM table_name"
# EQ_NAMES = pd.read_sql(query, conn)

# manual file if SQL connecrtion not available
EQ_NAMES = pd.read_csv("EQ_name_lookup.csv")

## Change working directory to where testing PDFs are located on your device
#os.chdir(r'C:\Path\To\Your\PDFs')

#DEFINE PDF to TEST
pid_pdf = 'filename.pdf'  #replace with your test PDF file name

## Save the results of running the model and the PDF name passed
results, pdf_name = locr.run_custom_model(endpoint='https://azure.com/',
                                         credential='credentialstring',
                                         model_id='modelid',
                                         pdf_path= 'pid_pdf'
)

#initialize empty dataframes
EQ_FRAME_1 = pd.DataFrame()
EQ_FRAME_2 = pd.DataFrame()
LINE_FRAME_1 = pd.DataFrame()
LINE_FRAME_2 = pd.DataFrame()                                                       

## Extract report data
EXTRACT_RESULTS,EXTRACT_ERRORS, EQ_FRAME_1, EQ_FRAME_2, LINE_FRAME_1, LINE_FRAME_2,  EQ_scan_full_tags, EQ_scan_cleaned_tags, possible_tags, confirmed_tags, lines_poly, confirmed_attributes, draw_poly = ocr.general_extract(results=results,
                                                       pdf_name=pdf_name,
                                                       EQ_FRAME_1 = EQ_FRAME_1,
                                                       EQ_FRAME_2 = EQ_FRAME_2,
                                                       LINE_FRAME_1 = LINE_FRAME_1,
                                                       LINE_FRAME_2 = LINE_FRAME_2,
                                                       EQ_NAMES = EQ_NAMES
)

#see highlights visualized on the PDFs
done = highlighter.highlight(pid_pdf, results, confirmed_tags, possible_tags, confirmed_attributes, lines_poly, draw_poly)

#equipment tags that we regex out of the neural model's full output
EQ_model_regex_tags = EXTRACT_RESULTS.iloc[0,2]
#everything the neural model labels as equipment tags and attributes
EQ_model_full_output = EXTRACT_RESULTS.iloc[0,0]

#equipment tags that are scanned twice on the page (and some other cleaning)
EQ_scan_cleaned_tags
#equipment tags that are scanned once on the page 
EQ_scan_full_tags

#line numbers are regex'd from a scan of every word on the page
Scan_LINE_numbers = EXTRACT_RESULTS.iloc[0,4]

#drawing number is reported directly from the neural model
model_DRAW_number = EXTRACT_RESULTS.iloc[0,6]

#polygon information
#polygon data for equipment tags labled by the model
confirmed_tags
#polygon data for scan equipment tags not labled by the model
possible_tags

#polygon data for line numbers, pulled by regex on scan
lines_poly

#polygon data for attributes seen by the neural model or twice by the scan
confirmed_attributes


# #==========================================================================================#
# # Write outputs to the excel (ONLY when completely done)
# writer = pd.ExcelWriter(pid_pdf, engine='xlsxwriter')

# EQ_FRAME_1.to_excel(writer, sheet_name='Sheet1', index=False)
# EQ_FRAME_2.to_excel(writer, sheet_name='Sheet2', index=False)
# LINE_FRAME_1.to_excel(writer, sheet_name='Sheet3', index=False)
# LINE_FRAME_2.to_excel(writer, sheet_name='Sheet4', index=False)

# # Save workbook
# writer.save()


#optional code split into two functions
# DF1, DF2, DF3, DF4, yellow, green, lines_coord, green_attribute, yellow_attribute = frames.dataframes( results=results,
#                                                         EQ_FRAME_1 = DF1,
#                                                        EQ_FRAME_2 = DF2,
#                                                        LINE_FRAME_1 = DF3,
#                                                        LINE_FRAME_2 = DF4,
#                                                        LOOKUP = LOOKUP)

