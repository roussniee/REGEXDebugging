# #master list of functions for name to run locally
# ##main branch stores all code needed to run locally

# credentials:

# sql database credentials are saved in 'credentials'
# each IP address has to be added to be able to connec
# without a connection, comment out that code in 'main'
# download the csv file EQ name lookup
# add "EQ_NAMES = pd.read_csv("EQ_name_lookup.csv")" to main before running extract errors
# local-ocr-functions connects to the azure neural model

# main:

# connects to sql database and pulls equipment tag names and abbreviations
# accesses results from Azure neural model including each pdf page's drawing number, equipment information, and line numbers.
# sends results to be parsed by "extract results" function
# sends pdf and results to be highlighted by "highlighter" function
# run everything from here by changing the applicable PDF name to whatever you want to test on (any pdf like PID # page #)
# ocr_functions:

# restructures results from Azure neural model
# uses ocr scan of the pdf
# confirms equipment tags and their associated information (dimensions, weight, etc called "attributes")
# also returns "possible" tags, which are information on the page that may or may not be an equipment piece
# defines line number tags
# regex at the top of the page labled for PID 1-5 is our most up to date pattern
# new line number regex is still being tested (will be committed later)
# highlighter:

# overlays the original pdf with highlights
# orange: confirmed equipment pieces and their attributes
# yellow: possible equipment pieces
# blue: line numbers
# pink: drawing number
# saves the new highlighted pdf as the original pdf's name _HL (for example, "PID-3-page-53_HL.pdf")
# does not work on any PID 7 at the moment (solution is being developed)
# azure-file:

# one long file with every needed function to run locally
# created only to test the azure pipeline


# Folder with PDFs
os.chdir(r'C:\Users\EConstantin\Documents\name\name_Testing\test8')

#grab equipment abbreviations and names
#EQ_NAMES = sql_connect()
#OR run without sql database connection
EQ_NAMES = pd.read_csv("EQ_name_lookup.csv")

# Accesses all files with .pdf or .PDF within the file listed in os.listdir(r'C:\...')
pdflist = []
ext = ('.PDF','.pdf')
no_ext = ("_HL.PDF", "_HL.pdf")
for files in os.listdir(r'C:\Users\EConstantin\Documents\name\name_Testing\test4'):
    if files.endswith(ext) == True and files.endswith(no_ext) == False:
        pdflist.append(files)
    else:
        continue
looper = len(pdflist)
# Hard code the number of iterations you would like with the line below in order to not loop through the entire PDF
#looper = 10
print(looper)

i = 0
while i < looper:

    pid_pdf = pdflist[i]
    print(pdflist[i])
    print(i)

    ## Save the results of running the model and the PDF name passed
    results, pdf_name = run_custom_model(endpoint='https://azure.com/',
                                            credential='credential',
                                            model_id='modelid',
                                            pdf_path= pid_pdf
    )

    #==================================================================================
    #for DEMO only without azure connections:
    excel_name = 'name_final_testing_output_5.xlsx'
    #load existing dataframe information 
    #if no existing data, (make new excel with 2 sheet tabs, reference it here)
    EQ_FRAME_1 = pd.read_excel(excel_name, sheet_name = 'Sheet1')
    EQ_FRAME_2 = pd.read_excel(excel_name, sheet_name = 'Sheet2')
    LINE_FRAME_1 = pd.read_excel(excel_name, sheet_name = 'Sheet3')
    LINE_FRAME_2 = pd.read_excel(excel_name, sheet_name = 'Sheet4')
    INSTRUMENTATION_DF = pd.read_excel(excel_name, sheet_name = 'Sheet5')

    #===================================================================================
                                           
    orientation_case = orientation(pid_pdf, results)
    print("orientation case: ", orientation_case)

    Drawing_Number, Drawing_Confidence, draw_poly = Drawing(results)
    print("drawing number: ",Drawing_Number)

    EQ_FRAME_1, EQ_FRAME_2, Equipment, EQ_Model_data, EQ_Scan_data, EQ_Scan_conf, EQ_Scan_poly, confirmed_tags, possible_tags, confirmed_attributes= Equipments(results, Drawing_Number, EQ_NAMES, EQ_FRAME_1, EQ_FRAME_2)
    print(EQ_FRAME_1)
    print(EQ_FRAME_2)
    print("model tags: ", EQ_Model_data)
    print("scanned tags: ", EQ_Scan_data)
    
    LINE_FRAME_1, LINE_FRAME_2, Line_Number, Line_conf, Line_poly = Lines(results, Drawing_Number, LINE_FRAME_1, LINE_FRAME_2)
    print(LINE_FRAME_1)
 
    INSTRUMENTATION_DF, Instrumentation_Final = Instrumentation(results, orientation_case, INSTRUMENTATION_DF, Drawing_Number)
    print(INSTRUMENTATION_DF)
    
    #see highlights visualized on the PDFs
    highlight(orientation_case, pid_pdf, confirmed_tags, possible_tags, confirmed_attributes, Line_poly, draw_poly, Instrumentation_Final)
    print("highlight completed)")
    # #==========================================================================================#
    # Write outputs to the excel (ONLY when completely done)
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')

    EQ_FRAME_1.to_excel(writer, sheet_name='Sheet1', index=False)
    EQ_FRAME_2.to_excel(writer, sheet_name='Sheet2', index=False)
    LINE_FRAME_1.to_excel(writer, sheet_name='Sheet3', index=False)
    LINE_FRAME_2.to_excel(writer, sheet_name='Sheet4', index=False)
    INSTRUMENTATION_DF.to_excel(writer, sheet_name='Sheet5', index=False)

    # Save workbook
    writer.save()

    i = i + 1
    
    
#MAIN MANUALLY======================================================================================
#grab equipment abbreviations and names
#EQ_NAMES = sql_connect()
#OR run without sql database connection
EQ_NAMES = pd.read_csv("EQ_name_lookup.csv")

# Folder with PDFs
os.chdir(r'C:\Users\EConstantin\Documents\name\name_Testing\test4')

#define test
PID = 7
page = 26
pid_pdf = pdf_builder(PID, page)

## Save the results of running the model and the PDF name passed
results, pdf_name = run_custom_model(endpoint='https://azure.com/',
                                         credential='credential',
                                         model_id='modelid',
                                         pdf_path= pid_pdf
)

#==================================================================================
# #for DEMO only without azure connections:
# excel_name = 'fixes_excel.xlsx'
# #load existing dataframe information 
# #if no existing data, (make new excel with 4 sheet tabs, reference it here)
# EQ_FRAME_1 = pd.read_excel(excel_name, sheet_name = 'Sheet1')
# EQ_FRAME_2 = pd.read_excel(excel_name, sheet_name = 'Sheet2')
# LINE_FRAME_1 = pd.read_excel(excel_name, sheet_name = 'Sheet3')
# LINE_FRAME_2 = pd.read_excel(excel_name, sheet_name = 'Sheet4')
# INSTRUMENTATION_DF = pd.read_excel(excel_name, sheet_name = 'Sheet5')

# #OR initialize empty dataframes
EQ_FRAME_1 = pd.DataFrame()
EQ_FRAME_2 = pd.DataFrame()
LINE_FRAME_1 = pd.DataFrame()
LINE_FRAME_2 = pd.DataFrame() 
INSTRUMENTATION_DF = pd.DataFrame()                                                      
# #===================================================================================

orientation_case, input_height, input_width = orientation(pid_pdf, results)

Drawing_Number, Drawing_Confidence, draw_poly = Drawing(results)

LINE_FRAME_1, LINE_FRAME_2, Line_Number, Line_conf, Line_poly = Lines(results, Drawing_Number, LINE_FRAME_1, LINE_FRAME_2)

EQ_FRAME_1, EQ_FRAME_2, Equipment, EQ_Model_data, EQ_Scan_data, EQ_Scan_conf, EQ_Scan_poly, confirmed_tags, possible_tags, confirmed_attributes= Equipments(results, Drawing_Number, EQ_NAMES, EQ_FRAME_1, EQ_FRAME_2, input_height, input_width)

INSTRUMENTATION_DF, Instrumentation_Final = Instrumentation(results, orientation_case, INSTRUMENTATION_DF, Drawing_Number)

#see highlights visualized on the PDFs
highlight(orientation_case, pid_pdf, confirmed_tags, possible_tags, confirmed_attributes, Line_poly, draw_poly, Instrumentation_Final)

# #==========================================================================================#
# # Write outputs to the excel (ONLY when completely done)
# writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')

# EQ_FRAME_1.to_excel(writer, sheet_name='Sheet1', index=False)
# EQ_FRAME_2.to_excel(writer, sheet_name='Sheet2', index=False)
# LINE_FRAME_1.to_excel(writer, sheet_name='Sheet3', index=False)
# LINE_FRAME_2.to_excel(writer, sheet_name='Sheet4', index=False)
# INSTRUMENTATION_DF.to_excel(writer, sheet_name='Sheet5', index=False)

# # Save workbook
# writer.save()

##########################################################################################
#                              All Libraries Used                                         #
##########################################################################################

from cmath import nan
import math
from operator import index
from unittest import result
from statistics import stdev
import io
import os
import json
import pandas as pd
import re
import numpy as np
import warnings
import pyodbc
#from credentials import name_sql
#import xlsxwriter
warnings.filterwarnings("ignore")
from asyncio.windows_events import NULL
from cmath import nan
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter, Transformation, PageObject, PdfFileMerger
from PyPDF2.generic import RectangleObject

from reportlab.graphics.shapes import Rect
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, red, yellow, green

#######FUNCTIONS======================================================================================================
##########################################################################################
#                             Drop Repeats                                               #
##########################################################################################

def dropRepeats(confirmedWords):
    
    #create dataframe
    wordDF = pd.DataFrame(confirmedWords, columns = ['word', 'x', 'y', 'width', 'height'])
    
    #truncate decimal values for corner x and y values
    # wordDF['x'] = round(wordDF['x'],1)
    # wordDF['y'] = round(wordDF['y'],1)
    
    # result = '{0:.3g}'.format(num)
    
    wordDF['x'] = wordDF['x']*100
    wordDF['y'] = wordDF['y']*100
    
    wordDF['x'] = np.trunc(wordDF['x'])
    wordDF['y'] = np.trunc(wordDF['y'])

    wordDF['x'] = wordDF['x']/100
    wordDF['y'] = wordDF['y']/100
    
    #drop duplicates on corner x and y value
    wordDF = wordDF.drop_duplicates(subset =['x', 'y'], keep = 'first')
    
    confirmedWords = list(wordDF)
    
    return confirmedWords

##########################################################################################
#                              On Side                                                   #
##########################################################################################
def OnSide(current_word, input_height, input_width, poly):
    # allWords = results['pages'][0]['words']
    # word = allWords[80]
    # current_word = word['content']
    # poly = word['polygon']

    if orientation_case in (1,6):  
        highx = input_height - .12*input_height
        highy = input_width -.12*input_width
        lowx = .12*input_height
        lowy = .12*input_width
    elif orientation_case in (2,7,3,5):  
        highy = input_height - .12*input_height
        highx = input_width - .12*input_width
        lowy = .12*input_height
        lowx = .12*input_width
    on_side = False
    
    centerx = ( poly[0]['x'] + poly[1]['x'] + poly[2]['x'] + poly[3]['x'] ) / 4
    centery = ( poly[0]['y'] + poly[1]['y'] + poly[2]['y'] + poly[3]['y'] ) / 4
    
    if (centery > lowy) and (centery < highy):
        if(centerx < lowx) or (centerx > highx):
            on_side = True
    else:
        on_side = False


    # if(poly[0]['x'] < lowx) or (poly[0]['x'] > highx):
    #     #if (poly[0]['y'] > lowy) or (poly[0]['y'] < highy):
    #         on_side = True
    # else:
    #     on_side = False
    
    return on_side

##########################################################################################
#                              Side Tags Off                                             #
##########################################################################################
# def SideTagsOff(orientation_case, EQ_Model_data, EQ_Scan_data, EQ_Scan_poly, non_slash_words):
#     if(orientation_case in (1, 2, 3, 5)):
#         # Hard coded bounds of the pages (would need to change for other pids later)
#         #goal: choose the bounds by the "to" and "from" PPID labels
#         lowx = 2
#         highx = 15

#         OutputTags = []
#         # OutputNoHighlight
#         if EQ_Scan_data != [] and EQ_Model_data != []:
#             OutputTags = EQ_Scan_data #+ EQ_Model_data

#         OutputPoly = EQ_Scan_poly
#         #i = EQ_Scan_poly[16]
#         for i in EQ_Scan_poly:
#             #if the eq scan poly tag is valid, continue
#             # if(len(i[1]) == 4):
#                 #j = EQ_Scan_data[0]
#                 #if the tag is in eq model data, keep it
#                 #else, if in eq scan data, (its possible that its on the sides)
#                 #if i in EQ_Scan_data:
#             if(i[1][0]['x'] < lowx) or (i[1][0]['x'] > highx):
#                 if(i in EQ_Scan_data or i in non_slash_words): #or i in EQ_Model_data):
#                     OutputTags.remove(i[0])
#                 # else:
#                 #     OutputNoHighlight.append(i)
       

#                 # for j in EQ_Scan_data:
#                 #     #if the poly entry is in scan data,
#                 #     if i[0] == j:
#                 #         # if(i[1][0] == "-"):   #this is removed with the initial eq scan ply check
#                 #         #     continue

#         #remove duplicates on a single list of tags
#         #error here when eq_scan_data has the wrong datatypes
#         #PID 2 35 has list[list[string]] which doesnt work
#         tempSet = set(OutputTags)
#         OutputTags = list(tempSet)
#         # print(OutputScan)
#     else:
#         OutputTags = EQ_Scan_data
#         OutputPoly = EQ_Scan_poly
        
#     return OutputTags, OutputPoly
    
##########################################################################################
#                              Get Words in Box                                          #
##########################################################################################
    
def get_words_in_box (Boundary=[], allWords=json):
    import json
    import pandas as pd
    validwords = []
    for word in allWords: 
        #word = allWords[190]
        try:
            word_box = word['bounding_box']
        except:
            word_box = word['polygon']
            
        centerx = ( word_box[0]['x'] + word_box[1]['x'] + word_box[2]['x'] + word_box[3]['x'] ) / 4
        centery = ( word_box[0]['y'] + word_box[1]['y'] + word_box[2]['y'] + word_box[3]['y'] ) / 4
        if centerx > Boundary[0]['x'] and centerx < Boundary[2]['x'] and True:
            xpass = True
        else: 
            xpass = False
        if centery > Boundary[0]['y'] and centery < Boundary[2]['y'] and True:
            ypass = True
        else:
            ypass = False
            
        inside_box = xpass and ypass and True
        if inside_box:
            #print(word['content'])
            validwords.append(word)
    return validwords

#instrumention
##########################################################################################
#                              Instrumentation                                           #
##########################################################################################
def Instrumentation(results, orientation_case, INSTRUMENTATION_DF, Drawing_Number):

    Instrument_REGEX = 'PSV|PSE|PRD'
    #Instrument_REGEX = '[1()\s]PSV[1()\s]|[1()\s]PSE[1()\s]|[1()\s]PRD[1()\s]'

    allWords = results['pages'][0]['words']
    # Instrumentation = []
    instrumentation_type = "Unknown"
    # Instrumentation_Conf = []
    Instrumentation_Info = []

    #get all instrumentation letters on the page
    #word = allWords[62]
    for word in allWords:
        current_word = word['content']
        current_conf = word['confidence']
        current_poly = word['polygon']
    
        current_instrumentation = re.findall(pattern = Instrument_REGEX, string = current_word)
        
        if current_instrumentation != []:
            for i in range(0, len(current_instrumentation)):
                #Instrumentation.append(current_instrumentation)
                if(current_instrumentation[0] == 'PSV'):
                    # print("TRUE")
                    instrumentation_type = 'PRESSURE SAFETY / RELIEF VALVE'
                    
                if (current_instrumentation[0] == 'PSE'):
                    instrumentation_type = 'RUPTURE DISC/ BUCKLING PIN'

                if (current_instrumentation[0] == 'PRD'):
                    instrumentation_type='PRESSURE RELIEF DEVICE'

                #do we want to add the 'PSE' substring, or the original word?
                #Instrumentation_Info.append([current_instrumentation[i], current_poly, instrumentation_type, current_conf])
                if len(current_word) < 5:
                    Instrumentation_Info.append([current_instrumentation[i], current_poly, instrumentation_type, current_conf])
                #Instrumentation_Poly.append([current_word, current_poly])

    #print(Instrumentation_Info)
                
    #get each instrumentation's associated numbers
    #entry = Instrumentation_Info[0]
    
    Instrumentation_Final = []
   # entry = Instrumentation_Info[0]
    for entry in Instrumentation_Info:
        current_instrumentation = entry[0]
        
        #make boundary box
        boundary = []
        boundary = [{'x':0, 'y':0},{'x':0, 'y':0},{'x':0, 'y':0},{'x':0, 'y':0}]
        
        if (orientation_case in (1,2,5)):
            #print("instrumentation for cases 1, 2, 5")
            #understand the orientation:
            #new x and y for a normal horizontal page PID
            # v_low_x = input_width_inch - entry[1][3]['y']     #highest y
            # v_high_x = input_width_inch - entry[1][1]['y']    #lowest y
            # v_low_y = input_height_inch - entry[1][2]['x']    #highest x
            # v_high_y = input_height_inch - entry[1][0]['x']   #lowest x

            #have to change every x and y corner
            boundary[0]['x'] = entry[1][0]['x']
            boundary[0]['y'] = entry[1][0]['y']
            boundary[1]['x'] = entry[1][1]['x']
            boundary[1]['y'] = entry[1][1]['y']
            boundary[2]['x'] = entry[1][2]['x']
            boundary[2]['y'] = entry[1][2]['y'] + .2
            boundary[3]['x'] = entry[1][3]['x'] 
            boundary[3]['y'] = entry[1][3]['y'] + .2
            
        # if(orientation_case == 2):
        #     #understand the orientation:
        #     #new x and y for a normal horizontal page PID
        #     # print("orientation case 2")
        #     # word = entry[0][0]
        #     # v_low_x = entry[1][3]['y']    #lowest y
        #     # v_high_x = entry[1][1]['y']   #highest y 
        #     # v_low_y = entry[1][2]['x']    #lowest x
        #     # v_high_y = entry[1][0]['x']   #highest x
            
        #     # boundary[0]['y'] -= .2
        #     # boundary[1]['y'] += .2
        
        #     # boundary[0]['x'] -= .2      
        #     # boundary[0]['y'] += .2
        #     # boundary[1]['x'] += .2
        #     # boundary[1]['y'] += .2
        #     #boundary[2]['x'] += .2
        #     boundary[2]['y'] += .2
        #    # boundary[3]['x'] -= .2
        #     boundary[3]['y'] += .2
            
        # if(orientation_case == 5):
        #     print("instrumentation case 5")
        #     #orientation understanding
        #     # lowest_x = entry[1][0]['x']
        #     # high_y = input_height_inch - entry[1][1]['y']
        #     # highest_x = entry[1][2]['x']
        #     # low_y = input_height_inch - entry[1][3]['y']

        #     # boundary[0]['x'] -= .2      
        #     # boundary[0]['y'] -= .2
        #     # boundary[1]['x'] += .2
        #     # boundary[1]['y'] -= .2
        #     # boundary[2]['x'] += .2
        #     boundary[2]['y'] += .2
        #     # boundary[3]['x'] -= .2
        #     boundary[3]['y'] += .2
    
        valid_words = get_words_in_box(boundary, allWords)
        #print(valid_words)
        
        numbers = []
        instrument_number_regex = '\d{2,5}[A-Z]?'
        #valid = valid_words[2]
        for valid in valid_words:
            current_number = re.findall(pattern = instrument_number_regex, string = valid['content'])
            #print(current_number)
            if current_number != []:
                numbers.append([current_number[0], valid['polygon']])
        
        if(numbers != []):
            # save the number to the current_instrumentation
            Instrumentation_Final.append([entry , numbers])
            #print([entry, numbers])
        elif(numbers == []):
            #preferable to not save any tags that dont have a number below them
            #PID 7 has "PSV" in a square with no number to identify them
            numbers = [[" "], [{'x':0, 'y':0},{'x':0, 'y':0},{'x':0, 'y':0},{'x':0, 'y':0}] ]
        
    
    # Create Instrumentation DF

    # #INSTRUMENTATION_DF = pd.DataFrame()                                                     
    # instrumentlength = (len(Instrumentation))
    # print(instrumentlength)
    # typelength = (len(Instrumentation_Type))
    # print(typelength)
    
    # i = 0
    # while i < instrumentlength:
    #     INSTRUMENTATION_DF = INSTRUMENTATION_DF.append({'Drawing Number': Drawing_Number, 'Instrumentation': Instrumentation[i], 'Instrumentation Type': Instrumentation_Type[i]}, ignore_index=True)
    #     i = i + 1
    
    #final = Instrumentation_Final[0]
    for final in Instrumentation_Final:
        if(len(final) > 1):
            name = final[0][0] + " " + final[1][0][0]
        elif(len(final) <= 1):
            name = final[0][0]
        INSTRUMENTATION_DF =  INSTRUMENTATION_DF.append({'Drawing Number': Drawing_Number, 'Instrumentation': name, 'Instrumentation Type': final[0][2], 'Instrumentation Confidence': final[0][3]}, ignore_index=True)

    # Return Values
    return INSTRUMENTATION_DF, Instrumentation_Final #, Instrumentation_Conf, Instrumentation_Info

##########################################################################################
#                              Pdf builder                                               #
##########################################################################################
#builds and returns string name for the pdf page
def pdf_builder(PID, page):
    if PID == 1:
        pid_pdf = "PID_PDF_page_" + str(page) + ".pdf"
    else:
        pid_pdf = "PID-" + str(PID) + "-page-" + str(page) + ".pdf"
    return pid_pdf

##########################################################################################
#                              SQL connect                                              #
##########################################################################################
def sql_connect():
    #credentials for sql server
    name_sql = {
        'server' : 'name-sql-server.database.windows.net',
        'database' : 'name-sql-db',
        'username' : 'AppUser',
        'password' : 'password',
        'driver' : '{ODBC Driver 17 for SQL Server}',
        'db_token' : ''
    }

    ## Connect to the SQL database
    connection_string = 'DRIVER='+name_sql['driver']+';SERVER='+name_sql['server']+';DATABASE='+name_sql['database']+';UID='+name_sql['username']+';PWD='+ name_sql['password']
    conn = pyodbc.connect(connection_string)

    ## Pull equipment abbreviations and names Table from SQL
    query = "SELECT Equipment_Type_Name, Equipment_Abbreviation FROM dbo.EQNAMELOOKUP"
    EQ_NAMES = pd.read_sql(query, conn)
    
    return EQ_NAMES

##########################################################################################
#                              is_ substring                                             #
##########################################################################################
#substring function
def sub_str(substring, string):
    if(string.find(substring) != -1):
        return True
    else:
        return False
    
##########################################################################################
#                              orientation                                          #
##########################################################################################
def orientation(pid_pdf, results):
    import PyPDF2
    from PyPDF2 import PdfFileReader, PdfFileWriter, Transformation, PageObject, PdfFileMerger
    from PyPDF2.generic import RectangleObject
    import io
    import os
    import pandas as pd

    from reportlab.graphics.shapes import Rect
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, red, yellow, green, orange

    # Define Input PDF 
    inputFile = pid_pdf

    # Define Reader and Output
    writer = PdfFileWriter()

    # Define inputPDF
    inputPDF = PdfFileReader(open(inputFile, "rb"))
    input = inputPDF.getPage(0)

    # Get Dimensions and Print
    input_height = float(input.mediabox.getHeight())/72
    input_width = float(input.mediabox.getWidth())/72

    # print("height: ")
    # print(input_height)
    # print("width")
    # print(input_width)
 
    #save first and last word
    allWords = results['pages'][0]['words']
    first_word = allWords[0]
    last_word = allWords[len(allWords)-1]
       
    #read in first word and last word from allWords results
    first_x = first_word['polygon'][0]['x']
    first_y = first_word['polygon'][0]['y']
    last_x = last_word['polygon'][0]['x']
    last_y = last_word['polygon'][0]['y']
    
    largest_x = 0
    largest_y = 0
    for word in allWords:
        x = word['polygon'][0]['x']
        y = word['polygon'][0]['y']
        if(x>largest_x):
            largest_x = x
        if(y>largest_y):
            largest_y = y
            
    # print(largest_x)
    # print(largest_y)
    
    #check for rotate first(x and y coordinates dont match)
    
    if ('/Rotate' in input.keys()):
        print("mediabox has 'Rotate'")
        #vertical or horizontal
        orientation = int(input['/Rotate'])

        #VERTICAL ENTRY NOTATIONS ==============
        if(orientation == 270):
            print("rotated 270")
            #like PID PDF page 32
            orientation_case = 1
            
        #90 degree read in (basically horizontal)
        if(orientation == 90):
            #similar to PID 8 page 40
            print("rotated = 90")
            orientation_case = 2
        
        if(orientation == 0):
            #topsoil pdfs
            print("rotated 0")
            orientation_case = 7
            
    #if rotate fails (x and y coordinates always match)
    if('/Rotate' not in input.keys()):
        
        if(first_x>last_x and last_y>first_y):
            print("decreasing x and increasing y")
            
            #get orientation using inches system
            if(largest_x > largest_y):
                print("horizontal orientation")
                #PID 7 (sometimes)
                orientation_case = 3
                
            if(largest_y >largest_x):
                print("vertical orientation")
                print("not set up yet")
                orientation_case =4
            
        #check for increasing x and y:
        if(first_x<last_x and last_y>first_y):
            print("increasing x and y")
            
            #check orientation
            if(largest_x>largest_y):
                print("horizontal orientation")
                orientation_case = 5
            
                    
            if(largest_y>largest_x):
                print("vertical orientation")
                print("not set up yet")
                orientation_case = 6
        
        else:
            #unknown orientation
            orientation_case = 0
            
    return orientation_case, input_height, input_width

##########################################################################################
#                              Highlight                                                 #
##########################################################################################
def highlight(orientation_case, pid_pdf, confirmed_tags, possible_tags, confirmed_attributes, Line_poly, draw_poly, INSTRUMENTATION_DF):
    import PyPDF2
    from PyPDF2 import PdfFileReader, PdfFileWriter, Transformation, PageObject, PdfFileMerger
    from PyPDF2.generic import RectangleObject
    import io
    import os
    import pandas as pd

    from reportlab.graphics.shapes import Rect
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, red, yellow, green, orange

    # Define Input PDF 
    inputFile = pid_pdf
    pid_pdf_str = pid_pdf.replace('.pdf', "")

    # Define Output Highlighter
    outputFile = str(pid_pdf_str) + "_HL.pdf"
    
    if(os.path.exists(outputFile)):
        os.remove(outputFile)
    
    # Define Reader and Output
    writer = PdfFileWriter()
    #merger = PyPDF2.PdfFileMerger()

    # Define inputPDF
    inputPDF = PdfFileReader(open(inputFile, "rb"))
    input = inputPDF.getPage(0)
    #input = PdfFileReader(open(inputFile, "rb")).getPage(0)

    # Get Dimensions and Print
    input_height = float(input.mediabox.getHeight())
    input_width = float(input.mediabox.getWidth())
    
    # Define Colors
    blueTransparent = Color(0, 80, 100, alpha=0.5)
    green50Transparent = Color(0, 100, 0, alpha=0.5)
    redTransparent = Color(0, 50, 20, alpha=0.5)
    pinkTransparent = Color(80, 0, 100, alpha=0.5)
    yellow50Transparent = Color(100, 100, 0, alpha=0.5)
    orangeTransparent = Color(.9, .5, .18, alpha=0.5)

    # Define Packet and Canvas Size
    packet = io.BytesIO()
    can = Canvas(packet, pagesize=(input_width, input_height))

    #there are 72 "points" in an inch
    input_height_inch = input_height/72
    input_width_inch = input_width/72
    
    confirmedWords = []
    possibleWords = []
    InstrumentWords = []
    lineNumbers = []
    drawingNumber = []
    
    #check for rotate first(x and y coordinates dont match)
    if(orientation_case == 0):
        print("orientation unknown")
        print("highlight not possible")
        
    if(orientation_case == 1):
        print("orientation case 1")
        
        confirmedWords = []
        if confirmed_tags != []:
            #entry = confirmed_tags[2]
            #len(entry[1])
            for entry in confirmed_tags:
                if(len(entry[1]) == 4):
                    word = entry[0]
                    v_low_x = input_width_inch - entry[1][3]['y']
                    v_high_x = input_width_inch - entry[1][1]['y']
                    v_low_y = input_height_inch - entry[1][2]['x']
                    v_high_y = input_height_inch - entry[1][0]['x']
                    
                    v_width = v_high_x - v_low_x
                    v_height = v_high_y - v_low_y
                    confirmedWords.append([word,v_low_x, v_low_y, v_width, v_height])

        
        if confirmed_attributes != []:
            for entry in confirmed_attributes:
                word = entry[1]
                v_low_x = input_width_inch - entry[2][3]['y']
                v_high_x = input_width_inch - entry[2][1]['y']
                v_low_y = input_height_inch - entry[2][2]['x']
                v_high_y = input_height_inch - entry[2][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                confirmedWords.append([word,v_low_x, v_low_y, v_width, v_height])
                
        #initialize yellow highlight list
        possibleWords = []
        #entry = possible_tags[3]
        if possible_tags != []:
            for entry in possible_tags:
                if(len(entry[1]) == 4):
                    word = entry[0]
                    v_low_x = input_width_inch - entry[1][3]['y']
                    v_high_x = input_width_inch - entry[1][1]['y']
                    v_low_y = input_height_inch - entry[1][2]['x']
                    v_high_y = input_height_inch - entry[1][0]['x']
                    
                    v_width = v_high_x - v_low_x
                    v_height = v_high_y - v_low_y
                    possibleWords.append([word,v_low_x, v_low_y, v_width, v_height])

        lineNumbers = []
        #entry = lines_coord[1]
        if(Line_poly != []):
            for entry in Line_poly:
                word = entry[0]
                v_low_x = input_width_inch - entry[1][3]['y']
                v_high_x = input_width_inch - entry[1][1]['y']
                v_low_y = input_height_inch - entry[1][2]['x']
                v_high_y = input_height_inch - entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                lineNumbers.append([word,v_low_x, v_low_y, v_width, v_height])
                
        InstrumentWords = []
        if(Instrumentation_Final != []):
            #final = Instrumentation_Final[1]
            #i = 1
            for final in Instrumentation_Final:
                #for both the letters and the numbers of the instrumentation,
                #should be in range 0 to 2, theres errors with that at the moment
                i = 0
                entry = final[0]
                word = entry[0]
                v_low_x = input_width_inch - entry[1][3]['y']
                v_high_x = input_width_inch - entry[1][1]['y']
                v_low_y = input_height_inch - entry[1][2]['x']
                v_high_y = input_height_inch - entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                InstrumentWords.append([word,v_low_x, v_low_y, v_width, v_height])

                if(len(final[1][0]) > 1):
                    i = 1
                    entry = final[1]
                    word = entry[0][0]
                    v_low_x = input_width_inch - entry[0][1][3]['y']
                    v_high_x = input_width_inch - entry[0][1][1]['y']
                    v_low_y = input_height_inch - entry[0][1][2]['x']
                    v_high_y = input_height_inch - entry[0][1][0]['x']
                    
                    v_width = v_high_x - v_low_x
                    v_height = v_high_y - v_low_y
                    InstrumentWords.append([word,v_low_x, v_low_y, v_width, v_height])

                    
        #drawing number highlighted in a different color
        drawingNumber = []
        entry = draw_poly

        v_low_x = input_width_inch - entry[3]['y']
        v_high_x = input_width_inch - entry[1]['y']
        v_low_y = input_height_inch - entry[2]['x']
        v_high_y = input_height_inch - entry[0]['x']
        
        v_width = v_high_x - v_low_x
        v_height = v_high_y - v_low_y
        drawingNumber.append([v_low_x, v_low_y, v_width, v_height])

    if(orientation_case == 2):   
        print("orientation case 2")
        confirmedWords = []
        
        if confirmed_tags != []:
            #entry = confirmed_tags[1]
            for entry in confirmed_tags:
                if(len(entry[1]) == 4):
                    word = entry[0]
                    v_low_x = entry[1][3]['y']
                    v_high_x = entry[1][1]['y']
                    v_low_y = entry[1][2]['x']
                    v_high_y = entry[1][0]['x']
                    
                    v_width = v_high_x - v_low_x
                    v_height = v_high_y - v_low_y
                    confirmedWords.append([word,v_low_x, v_low_y, v_width, v_height])
        
                
        if confirmed_attributes != []:
            for entry in confirmed_attributes:
                word = entry[1]
                v_low_x = entry[2][3]['y']
                v_high_x = entry[2][1]['y']
                v_low_y =  entry[2][2]['x']
                v_high_y = entry[2][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                confirmedWords.append([word,v_low_x, v_low_y, v_width, v_height])
                
        #initialize yellow highlight list
        possibleWords = []
        #entry = yellow_tags[3]
        if possible_tags != []:
            for entry in possible_tags:
                if(len(entry[1]) == 4):
                    word = entry[0]
                    v_low_x =  entry[1][3]['y']
                    v_high_x = entry[1][1]['y']
                    v_low_y =  entry[1][2]['x']
                    v_high_y =  entry[1][0]['x']
                    
                    v_width = v_high_x - v_low_x
                    v_height = v_high_y - v_low_y
                    possibleWords.append([word,v_low_x, v_low_y, v_width, v_height])

        lineNumbers = []
        #entry = lines_coord[1]
        if(Line_poly != []):
            for entry in Line_poly:
                word = entry[0]
                v_low_x =  entry[1][3]['y']
                v_high_x =  entry[1][1]['y']
                v_low_y =  entry[1][2]['x']
                v_high_y =  entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                lineNumbers.append([word,v_low_x, v_low_y, v_width, v_height])
                
        InstrumentWords = []
        if(Instrumentation_Final != []):
            #final = Instrumentation_Final[1]
            #i = 1
            for final in Instrumentation_Final:
                #print(final)
                #for both the letters and the numbers of the instrumentation,
                #should be in range 0 to 2, theres errors with that at the moment
                entry = final[0]
                word = entry[0]
                v_low_x = entry[1][3]['y']
                v_high_x = entry[1][1]['y']
                v_low_y = entry[1][2]['x']
                v_high_y = entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                InstrumentWords.append([word,v_low_x, v_low_y, v_width, v_height])

                if(len(final[1][0]) > 1):
                    entry = final[1][0]
                    word = entry[0]
                    v_low_x = entry[1][3]['y']
                    v_high_x = entry[1][1]['y']
                    v_low_y = entry[1][2]['x']
                    v_high_y = entry[1][0]['x']
                    
                    v_width = v_high_x - v_low_x
                    v_height = v_high_y - v_low_y
                    InstrumentWords.append([word,v_low_x, v_low_y, v_width, v_height])

                
        #drawing number highlighted in a different color
        drawingNumber = []
        entry = draw_poly

        v_low_x = entry[3]['y']
        v_high_x = entry[1]['y']
        v_low_y = entry[2]['x']
        v_high_y = entry[0]['x']
        
        v_width = v_high_x - v_low_x
        v_height = v_high_y - v_low_y
        drawingNumber.append([v_low_x, v_low_y, v_width, v_height])

    
    #if rotate fails (x and y coordinates always match)
    if(orientation_case == 3):  
        print("orientation case 3")
        #no rotate in input keys
        #decreasing x and increasing y
        #horizontal orientation
                 
        confirmedWords = []
        if confirmed_tags != []:
            for entry in confirmed_tags:
                word = entry[0][0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                confirmedWords.append([word, lowest_x, low_y, r_width, r_height])
        
        if confirmed_attributes != []:
            for entry in confirmed_attributes:
                word = entry[1]
                lowest_x = entry[2][0]['x']
                high_y = input_height_inch - entry[2][1]['y']
                highest_x = entry[2][2]['x']
                low_y = input_height_inch - entry[2][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                confirmedWords.append([word, lowest_x, low_y, r_width, r_height])
                
        #initialize yellow highlight list
        possibleWords = []
        #entry = yellow_tags[3]
        if possible_tags != []:
            for entry in possible_tags:
                word = entry[0][0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                possibleWords.append([word, lowest_x, low_y, r_width, r_height])
                
        lineNumbers = []

        if Line_poly != []:
            for entry in Line_poly:
                word = entry[0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                lineNumbers.append([word, lowest_x, low_y, r_width, r_height])
                
        
        InstrumentWords = []
        if(Instrumentation_Final != []):
            #final = Instrumentation_Final[1]
            #i = 1
            for final in Instrumentation_Final:
                #for both the letters and the numbers of the instrumentation,
                #should be in range 0 to 2, theres errors with that at the moment
                i = 0
                entry = final[0]
                word = entry[0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                InstrumentWords.append([word,v_low_x, v_low_y, v_width, v_height])

                if(len(final[1][0]) > 1):
                    i = 1
                    entry = final[1]
                    word = entry[0][0]        
                    lowest_x = entry[1][0]['x']
                    high_y = input_height_inch - entry[1][1]['y']
                    highest_x = entry[1][2]['x']
                    low_y = input_height_inch - entry[1][3]['y']
                    
                    r_width = highest_x - lowest_x
                    r_height = high_y - low_y
        
                    InstrumentWords.append([word,v_low_x, v_low_y, v_width, v_height])

                
        #drawing number coordinates are correct
        drawingNumber = []
        entry = draw_poly
        lowest_x = entry[0]['x']
        high_y = input_height_inch - entry[1]['y']
        highest_x = entry[2]['x']
        low_y = input_height_inch - entry[3]['y']
        
        r_width = highest_x - lowest_x
        r_height = high_y - low_y
        drawingNumber.append([lowest_x, low_y, r_width, r_height])
            
    if(orientation_case == 4):
        print("orientation case 4")
        #no rotate
        #decreasing x and increasing y
        #vertical orientation
        print("not set up yet")
                
                
    if(orientation_case == 5):
        print("orientation case 5")
        #no rotate
        #inreasing x and increasing y
        #horizontal orientation
            
        confirmedWords = []
        if confirmed_tags != []:
            for entry in confirmed_tags:
                word = entry[0][0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                confirmedWords.append([word, lowest_x, low_y, r_width, r_height])
        
        if confirmed_attributes != []:
            for entry in confirmed_attributes:
                word = entry[1]
                lowest_x = entry[2][0]['x']
                high_y = input_height_inch - entry[2][1]['y']
                highest_x = entry[2][2]['x']
                low_y = input_height_inch - entry[2][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                confirmedWords.append([word, lowest_x, low_y, r_width, r_height])
                
        #initialize yellow highlight list
        possibleWords = []
        #entry = yellow_tags[3]
        if possible_tags != []:
            for entry in possible_tags:
                word = entry[0][0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                possibleWords.append([word, lowest_x, low_y, r_width, r_height])
                
        lineNumbers = []

        if Line_poly != []:
            for entry in Line_poly:
                word = entry[0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
                
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                lineNumbers.append([word, lowest_x, low_y, r_width, r_height])
                
       
        InstrumentWords = []
        #no rotate
        #inreasing x and increasing y
        #horizontal orientation
        #final = Instrumentation_Final[0]
        if Instrumentation_Final != []:
            for final in Instrumentation_Final:
                #for both the letters and the numbers of the instrumentation,
                entry = final[0]
                word = entry[0]
                lowest_x = entry[1][0]['x']
                high_y = input_height_inch - entry[1][1]['y']
                highest_x = entry[1][2]['x']
                low_y = input_height_inch - entry[1][3]['y']
               
                r_width = highest_x - lowest_x
                r_height = high_y - low_y
                InstrumentWords.append([word, lowest_x, low_y, r_width, r_height])
                
                if(len(final[1][0]) > 1):
                    entry = final[1][0]
                    word = entry[0]
                    lowest_x = entry[1][0]['x']
                    high_y = input_height_inch - entry[1][1]['y']
                    highest_x = entry[1][2]['x']
                    low_y = input_height_inch - entry[1][3]['y']
                
                    r_width = highest_x - lowest_x
                    r_height = high_y - low_y
                    InstrumentWords.append([word, lowest_x, low_y, r_width, r_height])
                
        #drawing number coordinates are correct
        drawingNumber = []
        entry = draw_poly
        lowest_x = entry[0]['x']
        high_y = input_height_inch - entry[1]['y']
        highest_x = entry[2]['x']
        low_y = input_height_inch - entry[3]['y']
        
        r_width = highest_x - lowest_x
        r_height = high_y - low_y
        drawingNumber.append([lowest_x, low_y, r_width, r_height])

    if(orientation_case == 6):
        print("orientation case 6")
        #no rotate
        #increasing x and y
        #vertical orientation
        print("not set up yet")
        
    if(orientation_case == 7):
        print("orientation case 7")
        #no rotate
        #increasing x and y
        #vertical orientation
        print("not set up yet")
                
                
    
    #HIGHLIGHT=================================================================================
    # Create DFs
    # Define Canvas Highlighting
    
    HL = False
    if possibleWords != []:
        HL = True
        yellowWordsDF = pd.DataFrame(possibleWords)
        yellowWordsDF.columns = ['Word', 'x1', 'y1', 'width', 'height']
        can.setFillColor(yellow50Transparent)
        for i in range(len(yellowWordsDF)):
            can.rect(yellowWordsDF['x1'].iloc[i]*inch, yellowWordsDF['y1'].iloc[i]*inch, yellowWordsDF['width'].iloc[i]*inch, yellowWordsDF['height'].iloc[i]*inch, fill=True, stroke=False)
 
    if confirmedWords != []:
        #call new function to drop duplicated words
        #confirmedWords = dropRepeats(confirmedWords)
        HL = True
        orangeWordsDF = pd.DataFrame(confirmedWords)
        orangeWordsDF.columns = ['Word', 'x1', 'y1', 'width', 'height']
        can.setFillColor(orangeTransparent)
        for i in range(len(orangeWordsDF)):
            can.rect(orangeWordsDF['x1'].iloc[i]*inch, orangeWordsDF['y1'].iloc[i]*inch, orangeWordsDF['width'].iloc[i]*inch, orangeWordsDF['height'].iloc[i]*inch, fill=True, stroke=False)
        
    if drawingNumber != []:
        HL = True
        pinkWordsDF = pd.DataFrame(drawingNumber)
        pinkWordsDF.columns = ['x1', 'y1', 'width', 'height']
        can.setFillColor(pinkTransparent)
        can.rect(pinkWordsDF['x1'][0]*inch, pinkWordsDF['y1'][0]*inch, pinkWordsDF['width'][0]*inch, pinkWordsDF['height'][0]*inch, fill=True, stroke=False)
    
    if lineNumbers != []:
        HL = True
        blueWordsDF = pd.DataFrame(lineNumbers)
        blueWordsDF.columns = ['Word', 'x1', 'y1', 'width', 'height']
        can.setFillColor(blueTransparent)
        for i in range(len(blueWordsDF)):
            can.rect(blueWordsDF['x1'].iloc[i]*inch, blueWordsDF['y1'].iloc[i]*inch, blueWordsDF['width'].iloc[i]*inch, blueWordsDF['height'].iloc[i]*inch, fill=True, stroke=False)
    
    if InstrumentWords != []: 
        HL = True
        someWordsDF = pd.DataFrame(InstrumentWords)
        someWordsDF.columns = ['Word', 'x1', 'y1', 'width', 'height']
        can.setFillColor(pinkTransparent)
        for i in range(len(someWordsDF)):
            can.rect(someWordsDF['x1'].iloc[i]*inch, someWordsDF['y1'].iloc[i]*inch, someWordsDF['width'].iloc[i]*inch, someWordsDF['height'].iloc[i]*inch, fill=True, stroke=False)
    
    if HL == True:
        # Save Canvas
        can.save()

        # Find Canvas
        packet.seek(0)

        # Save Highlighted Canvas as PDF
        overlayPDF = PdfFileReader(packet)
        overlay = overlayPDF.getPage(0)
        
        input.mergePage(overlay)
        writer.add_page(input)
        writerStream = open(outputFile, "wb")
        writer.write(writerStream)
        writerStream.close()
    
##########################################################################################
#                              drawing number                                            #
##########################################################################################
def Drawing(results):
    Drawing_Number = results['documents'][0]['fields']['Drawing_Number']['content']
    
    if Drawing_Number == [] or Drawing_Number == None:
        pdf_index = pid_pdf.find("_publication.pdf")
        number_name = pid_pdf[:pdf_index]
        Drawing_Number = number_name
        Drawing_conf = 0
        draw_poly = [{'x':0, 'y':0},{'x':0, 'y':0},{'x':0, 'y':0},{'x':0, 'y':0}]
    else:
        Drawing_conf = results['documents'][0]['fields']['Drawing_Number']['confidence']
        draw_poly = results['documents'][0]['fields']['Drawing_Number']['bounding_regions'][0]['polygon']

    #save drawing number polygon data
    return Drawing_Number, Drawing_conf, draw_poly

##########################################################################################
#                              line    numbers                                         #
##########################################################################################
def Lines(results, Drawing_Number, LINE_FRAME_1, LINE_FRAME_2):
    #Line_regex = '[A]?\d{5,6}\-\w{0,4}\-?\d{2}[A-Z]{2}\d{2,3}[A-Z]?\(?[A-Z]?\/?\d{0,3}\)?\-[A-Z]{0,3}\-?\d{1,3}[\',\"]\-?\(?[A-Z]{0,3}\s?\d{0,3}\)?\-?\d?\s?\d?\/?\d?[\",\']?[A-Z]{0,2}\-?[A-Z]{0,2}\(?\.?\d{0,3}[\',\"]?[A-Z]?\.?[A-Z]?\)?\s?[A-Z]{0,2}\.?\d{0,2}\)?'
    #combined regex 1-5 and for 6
    #Line_regex = '[A]?\d{5,6}\-\w{0,4}\-?\d{2}[A-Z]{2}\d{2,3}[A-Z]?\(?[A-Z]?\/?\d{0,3}\)?\-[A-Z]{0,3}\-?\d{1,3}[\',\"]\-?\(?[A-Z]{0,3}\s?\d{0,3}\)?\-?\d?\s?\d?\/?\d?[\",\']?[A-Z]{0,2}\-?[A-Z]{0,2}\(?\.?\d{0,3}[\',\"]?[A-Z]?\.?[A-Z]?\)?\s?[A-Z]{0,2}\.?\d{0,2}\)?|\d{0,1}\s?\d{0,1}\/?\d{1}\"?\-[A-Z]{1,3}\-[A-Z]*\d*\-\d{1}\-[A-Z]{1}\d{2}[A-Z][a-z]?|\d{2,4}\-[A-Z]{0,2}\d{0,2}\-[A-Z]{1,2}\-?\d?[A-Z]*[\',\"]?'
    Line_regex = '[A]?\d{5,6}\-\w{0,4}\-?\d{2}[A-Z]{2}\d{2,3}[A-Z]?\(?[A-Z]?\/?\d{0,3}\)?\-[A-Z]{0,3}\-?\d{1,3}[\',\"]\-?\(?[A-Z]{0,3}\s?\d{0,3}\)?\-?\d?\s?\d?\/?\d?[\",\']?[A-Z]{0,2}\-?[A-Z]{0,2}\(?\.?\d{0,3}[\',\"]?[A-Z]?\.?[A-Z]?\)?\s?[A-Z]{0,2}\.?\d{0,2}\)?|\d{0,1}\s?\d{0,1}\/?\d{1}\"?\-[A-Z]{1,3}\-[A-Z]*\d*\-\d{1}\-[A-Z]{1}\d{2}[A-Z][a-z]?|\d{2,4}\-[A-Z]{0,2}\d{0,2}\-[A-Z]{1,2}\-?\d?[A-Z]*[\',\"]?|\d{1}\"\-[A-Z]{2,3}\-.{3,4}\-.{3}\-?1?|\d{1}\"\-[A-Z]\-[A-Z]{2}\-\d{5}|\d{5}\-\d{6}\-\d{2}[A-Z]{1,2}\d{3,4}\-\d{1,2}\"?\'?'
    
    #EQ_regex = '\d{5}\-\d{6}\-\d{2}[A-Z]{1,2}\d{3,4}\-\d{1,2}\"?\'?'
    #for PID set 6 (sort of)
    #PID 6 combined type 1 and type 2
    #Line_regex = '\d{0,1}\s?\d{0,1}\/?\d{1}\"?\-[A-Z]{1,3}\-[A-Z]*\d*\-\d{1}\-[A-Z]{1}\d{2}[A-Z][a-z]?|\d{2,4}\-[A-Z]{0,2}\d{0,2}\-[A-Z]{1,2}\-?\d?[A-Z]*[\",\']?'

    allWords = results['pages'][0]['words']
    Line_Number = []
    Line_conf = []
    Line_poly = []
    #word = allWords[6]
    #i = 10
    i = 0
    while i < len(allWords): 
        word = allWords[i]
        current_word = word['content']
        current_conf = word['confidence']
        current_poly = word['polygon']
    
        Line_word = re.findall(pattern = Line_regex, string = current_word)
    
        if Line_word != []:
            #is the next word a dimension for this line number?
            if((sub_str('"', allWords[i+1]['content']) == True) and (len(allWords[i+1]['content']) < 8)):
                #save the dimensions for the line number
                dim_word = allWords[i+1]['content']
                dim_poly = allWords[i+1]['polygon']
                #concatenate the line number with its dimensions
                line_string = Line_word[0]+ " " + dim_word
                line_string_list = [line_string]
                #save the "whole" line number and the coordinates for the extra dimensions
                Line_Number.append(line_string_list)
                Line_poly.append([dim_word, dim_poly])
                i += 1
            
            #if the line number does not have extra dimensions, save it 
            else:
                Line_Number.append(Line_word)
            
            Line_conf.append(current_conf)
            Line_poly.append([Line_word, current_poly])
            
        i += 1
        
    allLines = results['pages'][0]['lines']
    #Line_Number = []
    #Line_conf = []
    #Line_poly = []
    
    # # i =3
    # for i in range(0, len(allLines)): 
    #     word = allLines[i]
    #     current_word = word['content']
    #     #current_conf = word['confidence']
    #     current_poly = word['polygon']
    
    #     Line_word = re.findall(pattern = Line_regex, string = current_word)
    
    #     if Line_word != []:
    #         # #is the next word a dimension for this line number?
    #         # if((sub_str('"', allWords[i+1]['content']) == True) and (len(allWords[i+1]['content']) < 8)):
    #         #     #save the dimensions for the line number
    #         #     dim_word = allWords[i+1]['content']
    #         #     dim_poly = allWords[i+1]['polygon']
    #         #     #concatenate the line number with its dimensions
    #         #     line_string = Line_word[0]+ " " + dim_word
    #         #     line_string_list = [line_string]
    #         #     #save the "whole" line number and the coordinates for the extra dimensions
    #         #     Line_Number.append(line_string_list)
    #         #     Line_poly.append([dim_word, dim_poly])
    #         #     i += 1
            
    #         #if the line number does not have extra dimensions, save it 
    #         # else:
    #         Line_Number.append(Line_word)
            
    #         #Line_conf.append(current_conf)
    #         Line_poly.append([Line_word, current_poly])
    #     else:
    #         #try it with spaces removed
    #         line_no_spaces = current_word.replace(" ", "")
    #         Line_word = re.findall(pattern = Line_regex, string = line_no_spaces)
    #         if(Line_word != []):
    #             Line_Number.append(Line_word)
    #             Line_poly.append([Line_word, current_poly])
            
    #any need to drop duplicates on line numbers?
    #any need to use this line-by-line code and then shorten it to remove extra "duplicates"?
         
    #LINE NUMBER DATAFRAME 1
    #LINE_FRAME_1 = pd.DataFrame(columns = ['Drawing Number', 'Line Number'])
    for line in Line_Number:
        LINE_FRAME_1 = LINE_FRAME_1.append({'Drawing Number': Drawing_Number, 'Line Number': line}, ignore_index=True)

    #LINE NUMBER DATAFRAME 2
    #LINE_FRAME_2 = pd.DataFrame(columns = ['Line Number','Line Number Attribute', 'Line Number Value'])

    #line = Line_Number[5]
    for line in Line_Number:
        entry_number = 0
        string = line[0]
        
        #f_index = string.index('-')
        f_index = string.find('-')
        if(f_index != -1):
            facility = string[:f_index]
            string = string.replace(str(facility) + '-', "")
            entry_number += 1
            attribute = "Attribute #" + str(entry_number)
            #attribute = "Facility Location Code"
            LINE_FRAME_2 = LINE_FRAME_2.append({'Line Number': line, 'Line Number Attribute': attribute, 'Line Number Value': facility}, ignore_index=True)

        tag_index = string.find('-')
        if(tag_index != -1):
            tag = string[:tag_index]
            string = string.replace(str(tag)+'-', "")
            entry_number += 1
            attribute = "Attribute #" + str(entry_number)
            #attribute = 'Tag Number'
            LINE_FRAME_2 = LINE_FRAME_2.append({'Line Number': line, 'Line Number Attribute': attribute, 'Line Number Value': tag}, ignore_index=True)

        eq_index = string.find('-')
        eq = ""
        if(eq_index != -1):
            eq = string[:eq_index]
        if(eq != ""):
            rows = EQ_NAMES.loc[EQ_NAMES['Equipment_Abbreviation']==eq]
            if( rows.size != 0):
                type = rows['Equipment_Type_Name'].unique()
        else:
            type = 'Unknown'
        entry_number += 1
        attribute = "Attribute #" + str(entry_number)
        #attribute = 'Equipment Designation'
        LINE_FRAME_2 = LINE_FRAME_2.append({'Line Number': line, 'Line Number Attribute': attribute, 'Line Number Value': eq}, ignore_index=True)

        # inch_index = string.find('-')
        # if(inch_index != -1):
        #     inch = string[:inch_index]
        # string = string.replace(str(inch)+'-', "")
        # entry_number += 1
        # attribute = "Attribute #" + str(entry_number)
        # #attribute = 'Tag Number'
        # LINE_FRAME_2 = LINE_FRAME_2.append({'Line Number': line, 'Line Number Attribute': attribute, 'Line Number Value': tag}, ignore_index=True)
    
    return LINE_FRAME_1, LINE_FRAME_2, Line_Number, Line_conf, Line_poly



##########################################################################################
#                              Get Equiment                                              #
##########################################################################################
#EQUIPMENT tag and attributes

def Equipments(results, Drawing_Number, EQ_NAMES, EQ_FRAME_1, EQ_FRAME_2, input_height, input_width):
    ## Equipment
    Equipment_Headers = results['documents'][0]['fields']['Headers']['content']
    Equipment_Headers_conf = results['documents'][0]['fields']['Headers']['confidence']
    
    Equipment_Footers = results['documents'][0]['fields']['Footers']['content']
    Equipment_Footers_conf = results['documents'][0]['fields']['Footers']['confidence']
    
    ## If empty, make empty strings
    if Equipment_Headers == None:
        Equipment_Headers = " "
    if(Equipment_Footers == None):
        Equipment_Footers = " "
        
    Equipment = Equipment_Headers + " " + Equipment_Footers
    Equipment_conf = Equipment_Headers_conf*Equipment_Footers_conf

    #EQ regex 1-5 
    #EQ_regex = '[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d'
    #PID for 6, 8, 9 EQ regex
    #EQ_regex = '[A-Z]{1,3}\-[A-Z]?\d{3}\-?\d{0,4}'
    #regex for PID 7
    EQ_regex = '\d{5}\-[A-Z]{2}\d{2}\.\d{3}'

    #EQ_regex = '\d{1}\"\-[A-Z]\-[A-Z]{2}\-\d{5}'


    #don't drop duplicates because we want every instance of an EQ tag highlighted orange in the audience
    slash_words = []
    non_slash_words = []
    allLines = results['pages'][0]['lines']
    EQ_Scan_poly = []
    #line = allLines[275]
    for line in allLines:
        #index += 1
        current_word = line['content']
        #if this line is in the neural model Equipment output
        if sub_str(current_word, Equipment) == True:
            #save the tag without spaces to grab the original equipment tag
            current_word = current_word.replace(" ", "")
    
            #if there is an EQ tag in this line
            tag = re.findall(pattern = EQ_regex, string = current_word)
            if tag != []:
                #if this equipment tag has slashes,
                if(sub_str("/", current_word) == True):
                    #slash = True
                    #parse the current word into the word before the slash (first) and the rest of the word (next)
                    slash_index = current_word.find('/')
                    if(slash_index != -1):
                        first = current_word[:slash_index]
                        rest = current_word[slash_index:]
                        #remove the first slash in the remaining suffixes
                        rest = rest[1:]
                        
                        #if the suffix contains a full equipment tag, save it AND the original tag
                        suffix = re.findall(pattern=EQ_regex, string=rest)
                        if(suffix != False and suffix != []):
                            slash_words.append(suffix[0])
                            if(first == tag[0]):
                                slash_words.append(first)

                        elif(suffix == False or suffix == []):
                            #add the first as an equipment tag
                            slash_words.append(first)
                            
                            #add the full as a "never" allowed in the tags list
                            non_slash_words.append(tag[0])
                           
                            # #add the bare tag as a "never" allowed in the scanned tags list
                            # bare_regex = '[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\d{0,5}\-?\d{0,5}|[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\d{0,5}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d'
                            # bare = re.findall(pattern=bare_regex, string=current_word)
                            # non_slash_words.append(bare)
                            
                            #the suffix contains letters or numbers that need to be concatenated
                            while(rest != None):
                                #print(rest)
                                #if the rest of the word contains a slash, parse it
                                slash_index = rest.find('/')
                                if(slash_index != -1):
                                    #save the current suffix
                                    current_suffix = rest[:slash_index]
                                    #remove the first slash in the remaining word
                                    rest = rest[slash_index:]
                                    rest = rest[1:]
                                    finish = False 
                                else:
                                    current_suffix = rest
                                    finish = True
                                #if it contains letters, concatenate them as AB-1234A, AB-1234B
                                letters = re.findall(pattern='[A-Z]', string=current_suffix)
                                numbers = re.findall(pattern='\d', string=current_suffix)

                                #if it contains numbers, concatenate them as AB-1234, AB-5678
                                if (numbers != [] and len(numbers) < 3):
                                    #treat the numbers like letters and replace the end of the numbers
                                    new_tag = first[:(len(first) - len(current_suffix))]
                                    new_tag = new_tag + current_suffix
            
                                elif(numbers != [] and len(numbers) >= 3):
                                    #prefix = prefix.replace(last digits, current suffix)
                                    #grab the index of the hyphen or period
                                    hyphen_index = first.find('-')
                                    if hyphen_index != -1:
                                        #remove numbers after the last hyphen
                                        new_tag = first[:(hyphen_index+1)]
                                        #add the new numbers to make a new tag
                                        new_tag = new_tag + current_suffix
                                    period_index = first.find('.')
                                    if period_index != -1:
                                        #remove numbers after the last hyphen
                                        new_tag = first[:(period_index+1)]
                                        #add the new numbers to make a new tag
                                        new_tag = new_tag + current_suffix
                                    comma_index = first.find(',')
                                    if comma_index != -1:
                                        #remove numbers after the last hyphen
                                        new_tag = first[:(comma_index+1)]
                                        #add the new numbers to make a new tag
                                        new_tag = new_tag + current_suffix
                                        
                                elif letters != []:
                                    #remove last letter on the equipment tag
                                    new_tag = first [:(len(first)-1)]
                                    #add the letter as the new letter on the equipment tag
                                    new_tag = new_tag + current_suffix

                                if(new_tag):
                                    slash_words.append(new_tag)       
                                
                                if finish == True:
                                    rest = None
                else:
                    slash_words.append(current_word)

    neural_tags = re.findall(pattern = EQ_regex, string = Equipment)
    EQ_Model_data = []
    for entry in slash_words:
        if entry not in non_slash_words:
            EQ_Model_data.append(entry)
    for entry in neural_tags:
        if entry not in non_slash_words:
            EQ_Model_data.append(entry)
    
    EQ_TAGS = pd.DataFrame(EQ_Model_data)
    EQ_TAGS = EQ_TAGS.drop_duplicates()
    EQ_Model_data = EQ_TAGS.values.tolist()
            
    if(len(EQ_Model_data) >= 1):
        for i in range(0, len(EQ_Model_data)):
            EQ_Model_data[i] = EQ_Model_data[i][0]

    #remove instances of PID-1234 and AWP from MAWP from found model EQ words
    EQ_model_data_no_PID = list(EQ_Model_data)
    for word in EQ_Model_data:
        original_word = word
        word = str(word)
        if(sub_str('PID', word) == True):
            EQ_model_data_no_PID.remove(original_word)
        elif(sub_str('ID', word) == True):
            EQ_model_data_no_PID.remove(original_word)
        elif(sub_str('AWP', word) == True):
            EQ_model_data_no_PID.remove(original_word)
        elif(sub_str('ZZ', word) == True):
            EQ_model_data_no_PID.remove(original_word)
        elif(sub_str('KS', word) == True):
            EQ_model_data_no_PID.remove(original_word)
        elif(sub_str('XY', word) == True):
            EQ_model_data_no_PID.remove(original_word)
    EQ_Model_data = EQ_model_data_no_PID
    
    #drop duplicates on this list
    EQ_MODEL_FULL_DF = pd.DataFrame(EQ_Model_data)
    EQ_DROP_FULL = EQ_MODEL_FULL_DF.drop_duplicates()
    EQ_Model_data = EQ_DROP_FULL.values.tolist()
    
    #save every EQ tag as a string, not a list with one entry
    if(len(EQ_Model_data) >= 1):
        for i in range(0, len(EQ_Model_data)):
            EQ_Model_data[i] = EQ_Model_data[i][0]
        
    #SCAN all words on PDFs, classify as EQ
    # this was messy, trying to incorporate new slashing code
    allWords = results['pages'][0]['words']
    #EQ_Scan_poly = re.findall(pattern= EQ_regex, string= allWords)
    
    slash_words = []
    non_slash_scan_words = []
    # word = allWords[137]
    for word in allWords: 
        tag = ""
        current_word = word['content']
        current_conf = word['confidence']
        current_poly = word['polygon']

        #eliminate line numbers and other dimensions on the PDF
        if((sub_str('"', current_word)==False) and (sub_str("'", current_word)==False)):
            tag = re.findall(pattern = EQ_regex, string = current_word)         
           
            #if an equipment tag exists,
            if tag != []:
                
                EQ_Scan_poly.append([current_word, current_poly])

                if (tag in EQ_Model_data):
                    #save tag as confirmed (because its already been slashed out) and move on
                    slash_words.append([current_word, current_conf, current_poly])
                elif OnSide(current_word, input_height, input_width, poly=current_poly) == False:   
                    #squish the characters together
                    current_word = current_word.replace(" ", "")
                    slash = False
                    #does it contain a forward slash
                    if(sub_str("/", current_word) == True):
                        #squish the characters together
                        current_word = current_word.replace(" ", "")
                        slash = True
                        #parse the current word into the word before the slash (first) and the rest of the word (next)
                        slash_index = current_word.find('/')
                        if(slash_index != -1):
                            first = current_word[:slash_index]
                            rest = current_word[slash_index:]
                            #remove the first slash in the remaining suffixes
                            rest = rest[1:]

                            #if the suffix contains a full equipment tag, save it AND the original tag
                            suffix = re.findall(pattern=EQ_regex, string=rest)
                            if(suffix != False and suffix != []):
                                # slash_words.append(suffix[0])
                                slash_words.append([suffix[0], current_conf, current_poly])
                                if(first == tag[0]):
                                    # slash_words.append(first)
                                    slash_words.append([first, current_conf, current_poly])

                            elif(suffix == False or suffix == []):
                                #add the first as an equipment tag
                                # slash_words.append(first)
                                slash_words.append([first, current_conf, current_poly])
                                
                                # #add the bare tag as a "never" allowed in the scanned tags list
                                # bare_regex = '[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\d{0,5}\-?\d{0,5}|[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\d{0,5}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d'
                                # bare = re.findall(pattern=bare_regex, string=current_word)
                                # non_slash_words.append(bare)
                            
                                #add the bare tag as a "never" allowed in the tags list
                                non_slash_scan_words.append(current_word)

                                #the suffix contains letters or numbers that need to be concatenated
                                while(rest and rest != "" and rest != None):
                                    #print(rest)
                                    #if the rest of the word contains a slash, parse it
                                    slash_index = rest.find('/')
                                    if(slash_index != -1):
                                        #save the current suffix
                                        current_suffix = rest[:slash_index]
                                        
                                        #remove the first slash in the remaining word
                                        rest = rest[slash_index:]
                                        rest = rest[1:]
                                        finish = False 
                                    else:
                                        current_suffix = rest
                                        finish = True
                                    #if it contains letters, concatenate them as AB-1234A, AB-1234B
                                    letters = re.findall(pattern='[A-Z]', string=current_suffix)
                                    #if it contains numbers, concatenate them as AB-1234. AB-5678
                                    numbers = re.findall(pattern='\d', string=current_suffix)
                              
                                    if (numbers != [] and len(numbers) < 3):
                                        #treat the numbers like letters and replace the end of the numbers
                                        new_tag = first[:(len(first) - len(current_suffix))]
                                        new_tag = new_tag + current_suffix
                
                                    elif(numbers != [] and len(numbers) >= 3):
                                        #prefix = prefix.replace(last digits, current suffix)
                                        #grab the index of the hyphen or period
                                        hyphen_index = first.find('-')
                                        if hyphen_index != -1:
                                            #remove numbers after the last hyphen
                                            new_tag = first[:(hyphen_index+1)]
                                            #add the new numbers to make a new tag
                                            new_tag = new_tag + current_suffix
                                        period_index = first.find('.')
                                        if period_index != -1:
                                            #remove numbers after the last hyphen
                                            new_tag = first[:(period_index+1)]
                                            #add the new numbers to make a new tag
                                            new_tag = new_tag + current_suffix
                                        comma_index = first.find(',')
                                        if comma_index != -1:
                                            #remove numbers after the last hyphen
                                            new_tag = first[:(comma_index+1)]
                                            #add the new numbers to make a new tag
                                            new_tag = new_tag + current_suffix
                                    elif letters != []:
                                        #remove last letter on the equipment tag
                                        new_tag = first [:(len(first)-1)]
                                        #add the letter as the new letter on the equipment tag
                                        new_tag = new_tag + current_suffix
    
                                    if(new_tag):
                                        #EQ_Model_data.append(new_tag)
                                        slash_words.append([new_tag, 0, current_poly])
                                            
                                        
                                    if(new_tag):
                                        slash_words.append([new_tag, 0, current_poly])       
                                    
                                    if finish == True:
                                        rest = None
                    else:
                        slash_words.append([current_word, current_conf, current_poly])

                    
    # print("appending tags at the beginning of 1000")
    # print(tag)
    EQ_Scan_data = []
    EQ_Scan_conf = []
    #EQ_Scan_poly = []
    #entry = slash_words[1]
    for entry in slash_words:
        if entry[0] not in non_slash_scan_words:
            EQ_Scan_data.append(entry[0])
            EQ_Scan_conf.append(entry[1])
            #EQ_Scan_poly.append([entry[0],entry[2]])
            
    #combine non_slash_words
    if non_slash_scan_words != []:
        for entry in non_slash_scan_words:
            non_slash_words.append(entry)

    #remove instances of PPID-1234 and AWP-1234 and instruments BA- from scanned EQ tags
    #eventually make this remove any instrumentation abbreviation from a sql lookup
    EQ_Scan_data_no_PID = list(EQ_Scan_data)
    #word = EQ_Scan_data[4]
    for word in EQ_Scan_data:
        original_word = word
        word = str(word)
        if(sub_str('PID', word) == True):
            EQ_Scan_data_no_PID.remove(original_word)
        elif(sub_str('ID', word) == True):
            EQ_Scan_data_no_PID.remove(original_word)
        elif(sub_str('AWP', word) == True):
            EQ_Scan_data_no_PID.remove(original_word)
        elif(sub_str('ZZ', word) == True):
            EQ_Scan_data_no_PID.remove(original_word)
        elif(sub_str('KS', word) == True):
            EQ_Scan_data_no_PID.remove(original_word)
        elif(sub_str('XY', word) == True):
            EQ_Scan_data_no_PID.remove(original_word)
    EQ_Scan_data = EQ_Scan_data_no_PID

    #save a full list of EQ tags scanned
    #drop duplicates on this list
    EQ_Scan_full_data = EQ_Scan_data
    #then remove double instances of the repeated EQ's
    EQ_SCAN_FULL_DF = pd.DataFrame(EQ_Scan_full_data)
    EQ_DROP_FULL = EQ_SCAN_FULL_DF.drop_duplicates()
    EQ_Scan_full_data = EQ_DROP_FULL.values.tolist()
    
    #save every EQ tag as a string, not a list with one entry
    if(len(EQ_Scan_full_data) >= 1):
        for i in range(0, len(EQ_Scan_full_data)):
            EQ_Scan_full_data[i] = EQ_Scan_full_data[i][0]

    #keep duplicates
    EQ_SCAN_DF = pd.DataFrame(EQ_Scan_data)
    EQ_SCAN_duplicates = EQ_SCAN_DF[EQ_SCAN_DF.duplicated(keep=False)]
    EQ_Scan_data = EQ_SCAN_duplicates.values.tolist()

    #then remove double instances of the repeated EQ's
    EQ_SCAN_DF = pd.DataFrame(EQ_Scan_data)
    EQ_DROP = EQ_SCAN_DF.drop_duplicates()
    EQ_Scan_data = EQ_DROP.values.tolist()

    #save the tags as 'strings' not ['strings']
    if(len(EQ_Scan_data) > 0):
        for i in range(0, len(EQ_Scan_data)):
            EQ_Scan_data[i] = EQ_Scan_data[i][0]
            
    # OutputTags, OutputPoly = SideTagsOff(orientation_case, EQ_Model_data, EQ_Scan_data, EQ_Scan_poly, non_slash_words)
    # if(OutputTags != []):
    #     EQ_Scan_data = OutputTags
    # if(OutputPoly != []):
    #     EQ_Scan_poly = OutputPoly

    #define equipment tags that are confirmed (orange) or possible (yellow)
    confirmed_tags = []
    possible_tags = []

    #for tags that the scan saved, save their coordinates for highlighting
    #entry = EQ_Scan_poly[10]
    for entry in EQ_Scan_poly:
        tag = entry[0]
        cord = entry[1]
        if(tag in EQ_Model_data): #or tag[0] in EQ_Model_data):
            confirmed_tags.append([tag, cord])
        elif(sub_str(tag, Equipment) == True):
            confirmed_tags.append([tag, cord])
        elif(tag in EQ_Scan_data): #or tag[0] in EQ_Scan_data):
            possible_tags.append([tag, cord])
        # elif (tag in EQ_Scan_full_data or tag[0] in EQ_Scan_full_data):
        #     possible_tags.append([tag, cord])


    #MOVE to its own function like "build attributes"
    #DATA FRAME 2: EQ_FRAME_2   
    #
    confirmed_attributes = []
    allLines = results['pages'][0]['lines']
    for index in range(0,len(allLines)):
        current_line = allLines[index]['content']
        
        # if current_line in Equipment and current_line not in (EQ_Model_data, EQ_Scan_data):
        #     if len(current_line) > 5:
        #         current_poly = allLines[index]['polygon']
        #         confirmed_attributes.append([current_line, current_line, current_poly])
            
        #MODEL EQ ATTRIBUTES
        eq_tags = []
        eq_tags = re.findall(pattern = EQ_regex, string = current_line)
        
        #if the regex found an EQ tag IN the current line,
        if eq_tags != []:
            for tag in eq_tags:
                #print(tag)
                #if the tag is one that the model recognized
                if(tag in EQ_Model_data or tag in non_slash_words):
                    #print("in model")
                    #save all its attributes
                    attribute_counter = 0
                    #is the next line a valid attribute but not a new equipment tag,
                    
                    if( index < len(allLines)-1):
                        while( (allLines[index+1]['content'] in Equipment)and (allLines[index+1]['content'] not in EQ_Model_data)):
                            phrase = allLines[index+1]['content']
                            current_poly = allLines[index+1]['polygon']
                            if(len(phrase) > 1):    #save the attribute
                                attribute_counter += 1
                                attribute = "Attribute #" + str(attribute_counter)
                                EQ_FRAME_2 = EQ_FRAME_2.append({'Equipment Tag': tag, 'Equipment Attribute': attribute, 'Equipment Value': phrase}, ignore_index=True)
                                confirmed_attributes.append([current_line, phrase, current_poly])
                            index += 1  #check the next line 
                        index += 1
                    
                #SCANNED EQ ATTRIBUTES
                #if this is a scanned EQ tag that's seen twice, mark it green
                # elif(tag in EQ_Scan_data):
                #     # print("in scan")
                #     # save the line following the tag (usually the name of the machine)
                #     tag = current_line
                #     phrase = allLines[index+1]['content']
                #     current_poly = allLines[index+1]['polygon']
                #     if((phrase not in EQ_Scan_data) and (len(phrase) > 5)):  
                #         attribute = "Attribute #1"
                #         EQ_FRAME_2 = EQ_FRAME_2.append({'Equipment Tag': tag, 'Equipment Attribute': attribute, 'Equipment Value': phrase}, ignore_index=True)
                #         confirmed_attributes.append([current_line, phrase, current_poly])
                #     index += 1
                #if this is a scanned EQ tag that's seen ONCE, mark it yellow
                # elif(tag in EQ_Scan_full_data):
                #     #print("in full scan")
                #     #save the line following the tag (usually the name of the machine)
                #     #tag = current_line
                #     phrase = allLines[index+1]['content']
                #     current_poly = allLines[index+1]['polygon']
                #     if((phrase not in EQ_Scan_data) and (len(phrase) > 5)):  
                #         attribute = "Attribute #1"
                #         EQ_FRAME_2 = EQ_FRAME_2.append({'Equipment Tag': tag, 'Equipment Attribute': attribute, 'Equipment Value': phrase}, ignore_index=True)
                #         # yellow_attribute.append([current_line, phrase, current_poly])
                #     index += 1 
                else:
                    #line is not an EQ tag, continue to next line
                    index += 1 
        else:
            index += 1        

        
    #ERRORS here. sometimes wont run!!!!
    #issues with the abbreviations look up
    #possible datatype mismatches
    #EQUIPMENT DATAFRAME 1
    # tag = EQ_Model_data[1]
    #tag = possible_tags[0]
    #tag = EQ_Model_data[0]
    for tag in EQ_Model_data:
    
          
        # #first, determine punctuation
        # if sub_str("-", tag) == True:
        #     index = tag.find('-')
        # elif sub_str(".", tag) == True:                      
        #     index = tag.find('.')
        # elif sub_str(",", tag) == True:
        #     index = tag.find(',')
        # else:
        #     index = 2
            
        # abbreviation = tag[:index]
        
        # #clean up abbreviation 
        # #remove parenthesis, numbers, etc
        
        # rows = EQ_NAMES.loc[EQ_NAMES['Equipment_Abbreviation']==abbreviation]
        # if( rows.size != 0):
        #     type = rows['Equipment_Type_Name'].unique()
        #     #type = type[0]
        #     type = type[0].replace('\xa0', " ")
        # else:
        type = 'Unknown'
        #type = 'Model'
       
        EQ_FRAME_1 = EQ_FRAME_1.append({'Drawing Number': Drawing_Number, 'Equipment Type':type, 'Equipment Tag': tag}, ignore_index=True)
    
    #tag = EQ_Scan_data[0]
    for tag in EQ_Scan_data:
        # if( tag not in EQ_Model_data): 
        #     abbreviation = tag[:2]
        #     rows = EQ_NAMES.loc[EQ_NAMES['Equipment_Abbreviation']==abbreviation]
        #     if( rows.size != 0):
        #         type = rows['Equipment_Type_Name'].unique()
        #         type = type[0].replace('\xa0', " ")
        #     else:
        type = 'Unknown'
        #type = 'Scan'
                
        EQ_FRAME_1 = EQ_FRAME_1.append({'Drawing Number': Drawing_Number, 'Equipment Type':type, 'Equipment Tag': tag}, ignore_index=True)
        
    EQ_FRAME_1 = EQ_FRAME_1.drop_duplicates()
    
    return EQ_FRAME_1, EQ_FRAME_2, Equipment, EQ_Model_data, EQ_Scan_data, EQ_Scan_conf, EQ_Scan_poly, confirmed_tags, possible_tags, confirmed_attributes


###############
# run_ocr
###############

def run_ocr(endpoint,credential,pdf_path,export_location=None):
    """
    ----------
    Description
    ----------
        Runs OCR on specified file
    
    ----------
    Parameters
    ----------
        endpoint : str
            Your Azure endpoint URL
        credential : str
            Your Azure credential
        pdf_path : str
            Path to the PDF to run through the model
        export_location : str, optional
            Path to export the JSON file (if desired)
    ----------
    Returns
    -------
        dict
            Model results in dictionary format
        json
            If `export_location` is specified, a json file
            is outputted.    
    """
    
    ## Packages
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient
    import os 
    import json
    
    ## Make `credential` as Azure credential
    credential = AzureKeyCredential(credential)
    
    ## Create `DocumentAnalysisClient`
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint,credential=credential)
    
    ## Run the model
    with open(pdf_path, 'rb') as f:
        poller = document_analysis_client.begin_analyze_document(
            'prebuilt-layout', document=f
        )
        
    ## Save the results of the model
    result = poller.result()
    
    ## Convert the results into a dictionary (JSON organization)
    result = result.to_dict()
    
    ## If export_location is specified, save the file as a json
    if export_location != None:
        filename = os.path.basename(pdf_path) ## Pull out the filename
        os.chdir(export_location) ## Change working directory to `export_location`
        
        ## Save json file
        
        with open(os.path.join(export_location,filename+'.ocr.json'),'w',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=4)

    return(result)

###############
# run_custom_model
###############

def run_custom_model(endpoint,credential,model_id,pdf_path,export_location=None):
    """
    ----------
    Description
    ----------
        Runs custom Azure Form Recognizer model on specified file
    
    ----------
    Parameters
    ----------
        endpoint : str
            Your Azure endpoint URL
        credential : str
            Your Azure credential
        model_id : str
            The model id of the model to run
        pdf_path : str
            Path to the PDF to run through the model
        export_location : str, optional
            Path to export the JSON file (if desired)
    ----------
    Returns
    -------
        dict
            Model results in dictionary format
        str
            The name of the PDF passed
        json
            If `export_location` is specified, a json file
            is outputted.    
    """
    
    ## Packages
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient
    import os
    import json
    
    ## Make `credential` an Azure credential
    credential = AzureKeyCredential(credential)
    
    ## Create `DocumentAnalysisClient`
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint,credential=credential)
    
    ## Run the model
    with open(pdf_path,'rb') as f:
        poller = document_analysis_client.begin_analyze_document(
            model_id=model_id,document=f
        )
    
    ## Save the results of the model
    result = poller.result()
    
    ## Convert results into a dicitonary (JSON organization)
    result = result.to_dict()
    
    ## If `export_location` is specified, save the file as a json
    if export_location != None:
        filename = os.path.basename(pdf_path) ## Pull out the filename
        
        ## Save json file
        with open(os.path.join(export_location,filename+'.labels.json'),'w',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=4)
    
    ## Extrat the pdf_name
    pdf_name = os.path.basename(pdf_path)
    
    return result, pdf_name