#azure file to upload

#all libraries

from cmath import nan
from operator import index
#import ocr_functions as ocr
#import local_ocr_functions as locr
#import highlighter
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
#from cmath import nan
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter, Transformation, PageObject, PdfFileMerger
from PyPDF2.generic import RectangleObject

from reportlab.graphics.shapes import Rect
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep, Color, red, yellow, green

#SQl connection credentials
name_sql = {
    'server' : 'name-sql-server.database.windows.net',
    'database' : 'name-sql-db',
    'username' : 'AppUser',
    'password' : '[password]',
    'driver' : '{ODBC Driver 17 for SQL Server}',
    'db_token' : ''
}

## Connect to the SQL database
connection_string = 'DRIVER='+name_sql['driver']+';SERVER='+name_sql['server']+';DATABASE='+name_sql['database']+';UID='+name_sql['username']+';PWD='+ name_sql['password']
conn = pyodbc.connect(connection_string)

## Pull Equipment Abbreviations and Names Table from SQL
query = "SELECT Equipment_Type_Name, Equipment_Abbreviation FROM dbo.EQNAMELOOKUP"
EQ_NAMES = pd.read_sql(query, conn)

#AZURE local funtions (whose outputs need to be replaced)
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


#IMPORTANT. the regex pattern that is looked for in the models
#EQ_regex = '[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?\(?[A-Z]{1,2}\-\d{4,5}\)?\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d|TK-\d{4}|BL-\d{4}|SE\.\d{2}\.\d{4}|CV-\d{4}|CE-\d{4}|CO-\d{4}|C0-\d{4}|AC-CO-\d{4}|P-CO-\d{4}|CM-\d{4}|CZ-\d{4}\-\d|AC-\d{4}\-\d|CO\.\d{2}\.\d{4}|CM\.\d{2}\.\d{4}|AC-\d{4}|HT\.\d{2}\.\d{4}|CT-\d{4}|CR-\d{4}|EG-\d{4}|EM-\d{4}|FN-\d{4}|FL-\d{4}|F-\d{4}|F-CO-\d{4}|FL\d{2}[.,]\d{4}|FG-\d{4}|FS-\d{4}|GT-\d{4}|GB-\d{4}|HE-\d{4}|HR-\d{4}|HR\d{2}[.,]\d{4}|HB-\d{4}|HTR-\d{4}|H-\d{4}|MX-\d{4}|M-\d{5}|M-/M-\d{4,5}|NO-\d{4}|PI-\d{4}|PT-\d{4}|PV-\d{4}|PR\d{2}[.,]\d{4}|PU-\d{4}|PM[.,]\d{2}[.,]\d{4}|PM\d{2}\.\d{4}|PR-\d{4}|TR-\d{4}|SK-\d{4}|ST-\d{4}|SR-\d{4}|S-\d{4}|SP-\d{4}|WC-\d{4}|CS-\d{4}|SW-\d{4}|TC-\d{4}|DU\.\d{2}\.\d{4}|TE-\d{4}|TU-\d{4}|UP-\d{4}|UCP-\d{4}|UC-\w\d{4}|UC\w?\-[A-Z]{0,2}\-\d{4}|VE-\d{4}|WI-\d{4}|FE-\d{4}|BPV-\d{4}|GC-\d{4}|M-\d{5}|MM-\d{2}|BM-\w{2}\d{4}|F-\d{2}|NG-\d{4}|G-\d{4}|MS-\d{2}|EH-\d{4}|EH-\d{2}|FL-|M-/M-'
#working for PID 1-5:
EQ_regex = '[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d'

#PID 6 and on in development:
#EQ_regex = '[A-Z]?\-?[A-Z]{1,2}\-\d{3,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d'

#DEFINE PDF file name to test 
#needs to be overwritten with the PDF name from the PDF splitter
pid_pdf = 'PID-6-page-16.pdf'

## Save the results of running the neural custom model and the PDF name passed
results, pdf_name = run_custom_model(endpoint='https://azure.com/',
                                         credential='credential',
                                         model_id='modelid',
                                         pdf_path= pid_pdf
)

#azure OCR function
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

#search string for substring, return true if found
def sub_str(substring, string):
    if(string.find(substring) != -1):
        return True
    else:
        return False
    
def general_extract(results,pdf_name,EQ_FRAME_1, EQ_FRAME_2, LINE_FRAME_1, LINE_FRAME_2, EQ_NAMES):
    """
    ----------
    Description
    ----------
        Extracts report data from Azure Form Recognizer results
        uses OCR scan to further extract information from the P&ID PDFs
    
    ----------
    Parameters
    ----------
        results : dict
            Results of Azure Form Recognizer in dictionary form
        pdf_name : str
            Filename of the PDF passed
        EQ_FRAME_1: 
            dataframe with columns Drawing Number, Equipment Type, Equipment Tag ID
        EQ_FRAME_2: 
            dataframe with columns Equipment Tag ID, Attribute, Attribute value
        LINE_FRAME_1: 
            dataframe with columns Drawing Number, Line Number
        LINE_FRAME_2: 
            dataframe with columns Line Number, Attribute, Attribute Value
        LOOKUP:
            SQl database with columns Equipment type name and equipment abreviation 
        
    ----------
    Returns
    -------
        DATA : dataframe
            Azure Form Recognizer results in a pandas dataframe
        ERROR_LOG : dataframe
            Dataframe containing list of errors found in extraction
        EQ_FRAME_1: 
            dataframe with columns Drawing Number, Equipment Type, Equipment Tag ID
        EQ_FRAME_2: 
            dataframe with columns Equipment Tag ID, Attribute, Attribute value
        LINE_FRAME_1: 
            dataframe with columns Drawing Number, Line Number
        LINE_FRAME_2: 
            dataframe with columns Line Number, Attribute, Attribute Value
        yellow:
            list with possible equipment tags and their polygon corner data
        green:
            list with confirmed equipment tags and their polygon corner data
        line_poly:
            line numbers found by the scan and their polygon data
        attribute_poly:
            attributes as displayed in EQ_FRAME_2 and their polygon data

    """
    ## Initialize error_log
    error_log = []
    
    ## try/except error catching
    #main try for general python errors
    try:
        
        #Drawing number
        try:
            ## Drawing Number
            Drawing_Number = results['documents'][0]['fields']['Drawing_Number']['content']
            Drawing_conf = results['documents'][0]['fields']['Drawing_Number']['confidence']
            
            #save drawing number polygon data
            draw_poly = results['documents'][0]['fields']['Drawing_Number']['bounding_regions'][0]['polygon']
        
        except:
            ## Drawing Number Logic Check
            if Drawing_Number == None:
                error_log.append(['Extract','Drawing Number','Drawing Number could not be extracted'])
            else:
                None
                
        ## Line Number
        try: 
            allWords = results['pages'][0]['words']
            Line_Number = []
            Line_conf = []
            line_poly = []
            #word = allWords[20]
            for word in allWords: 
                current_word = word['content']
                current_conf = word['confidence']
                current_poly = word['polygon']
                #line_regex = '[A]?\d{5,6}\-\d{0,4}\-?\d{2} \C\S\d{3}[A-Z]?\(?[A-Z]?\/?\d{0,3}\)?\-[A-Z]{0,3}\-?\d{1,3}\"\-?\(?[A-Z]{0,3}\s?\d{0,3}\)?\-?\d?\s?\d?\/?\d?\"?[A-Z]{0,2}'
                Line_regex = '[A]?\d{5,6}\-\w{0,4}\-?\d{2}[A-Z]{2}\d{3}[A-Z]?\(?[A-Z]?\/?\d{0,3}\)?\-[A-Z]{0,3}\-?\d{1,3}\"\-?\(?[A-Z]{0,3}\s?\d{0,3}\)?\-?\d?\s?\d?\/?\d?\"?[A-Z]{0,2}\-?[A-Z]{0,2}\(?\.?\d{0,3}\"?[A-Z]?\.?[A-Z]?\)?\s?[A-Z]{0,2}\.?\d{0,2}\)?'
                #for PID set 6 (sort of)
                #Line_regex = '\d{3,4}\-[A-Z]\d{1}\-[A-Z]{2}[-,\s]\d{1}\"'
                Line_word = re.findall(pattern = Line_regex, string = current_word)
            
                if Line_word != []:
                    Line_Number.append(Line_word)
                    Line_conf.append(current_conf)
                    line_poly.append([Line_word, current_poly])             
        
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
                if(eq_index != -1):
                    eq = string[:eq_index]
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

        except Exception as e:###
            error_log.append(['Extraction','Line Number',e])  
    
        #EQUIPMENT tag and attributes
        try:
            ## Equipment
            Equipment = results['documents'][0]['fields']['Equipment_Tag']['content']
            Equipment_conf = results['documents'][0]['fields']['Equipment_Tag']['confidence']
            
            ## Logic Check Equipment
            if Equipment == None:
                Equipment = " "
        
            #pull regex pattern from excel, paste it as a string in EQ_model_regex
            #REGEX = pd.read_csv("name_regex_lookup.csv")
            #EQ_model_regex = REGEX['Equipment Regex Text Only']
            #EQ_model_word = re.findall(pattern = '|'.join(EQ_model_regex), string = Equipment)
            #print('|'.join(EQ_model_regex))
            
            #new regex with NO parentheses
            #EQ_model_regex = '[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?[A-Z]{1,2}\-\d{4,5}\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d|TK-\d{4}|BL-\d{4}|SE\.\d{2}\.\d{4}|CV-\d{4}|CE-\d{4}|CO-\d{4}|C0-\d{4}|AC-CO-\d{4}|P-CO-\d{4}|CM-\d{4}|CZ-\d{4}\-\d|AC-\d{4}\-\d|CO\.\d{2}\.\d{4}|CM\.\d{2}\.\d{4}|CM\.\d{2}\.\d{4}|AC-\d{4}|HT\.\d{2}\.\d{4}|CT-\d{4}|CR-\d{4}|EG-\d{4}|EM-\d{4}|FN-\d{4}|FL-\d{4}|F-\d{4}|F-CO-\d{4}|FL\d{2}[.,]\d{4}|FG-\d{4}|FS-\d{4}|GT-\d{4}|GB-\d{4}|HE-\d{4}|HR-\d{4}|HR\d{2}[.,]\d{4}|HB-\d{4}|HTR-\d{4}|H-\d{4}|MX-\d{4}|M-\d{5}|M-/M-\d{4,5}|NO-\d{4}|PI-\d{4}|PT-\d{4}|PV-\d{4}|PR\d{2}[.,]\d{4}|PU-\d{4}|PM[.,]\d{2}[.,]\d{4}|PM\d{2}\.\d{4}|PR-\d{4}|TR-\d{4}|SK-\d{4}|ST-\d{4}|SR-\d{4}|S-\d{4}|SP-\d{4}|WC-\d{4}|CS-\d{4}|SW-\d{4}|TC-\d{4}|DU\.\d{2}\.\d{4}|TE-\d{4}|TU-\d{4}|UP-\d{4}|UCP-\d{4}|UC-\w\d{4}|UC\w?\-[A-Z]{0,2}\-\d{4}|VE-\d{4}|WI-\d{4}|FE-\d{4}|BPV-\d{4}|GC-\d{4}|M-\d{5}|MM-\d{2}|BM-\w{2}\d{4}|F-\d{2}|NG-\d{4}|G-\d{4}|MS-\d{2}|EH-\d{4}|EH-\d{2}|FL-|M-/M-'
            #EQ_model_regex = '[A-Z]?\-?\(?[A-Z]{1,2}\-\d{3,5}\)?\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?\(?[A-Z]{1,2}\-\d{3,5}\)?\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d|TK-\d{4}|BL-\d{4}|SE\.\d{2}\.\d{4}|CV-\d{4}|CE-\d{4}|CO-\d{4}|C0-\d{4}|AC-CO-\d{4}|P-CO-\d{4}|CM-\d{4}|CZ-\d{4}\-\d|AC-\d{4}\-\d|CO\.\d{2}\.\d{4}|CM\.\d{2}\.\d{4}|AC-\d{4}|HT\.\d{2}\.\d{4}|CT-\d{4}|CR-\d{4}|EG-\d{4}|EM-\d{4}|FN-\d{4}|FL-\d{4}|F-\d{4}|F-CO-\d{4}|FL\d{2}[.,]\d{4}|FG-\d{4}|FS-\d{4}|GT-\d{4}|GB-\d{4}|HE-\d{4}|HR-\d{4}|HR\d{2}[.,]\d{4}|HB-\d{4}|HTR-\d{4}|H-\d{4}|MX-\d{4}|M-\d{5}|M-/M-\d{4,5}|NO-\d{4}|PI-\d{4}|PT-\d{4}|PV-\d{4}|PR\d{2}[.,]\d{4}|PU-\d{4}|PM[.,]\d{2}[.,]\d{4}|PM\d{2}\.\d{4}|PR-\d{4}|TR-\d{4}|SK-\d{4}|ST-\d{4}|SR-\d{4}|S-\d{4}|SP-\d{4}|WC-\d{4}|CS-\d{4}|SW-\d{4}|TC-\d{4}|DU\.\d{2}\.\d{4}|TE-\d{4}|TU-\d{4}|UP-\d{4}|UCP-\d{4}|UC-\w\d{4}|UC\w?\-[A-Z]{0,2}\-\d{4}|VE-\d{4}|WI-\d{4}|FE-\d{4}|BPV-\d{4}|GC-\d{4}|M-\d{5}|MM-\d{2}|BM-\w{2}\d{4}|F-\d{2}|NG-\d{4}|G-\d{4}|MS-\d{2}|EH-\d{4}|EH-\d{2}|FL-|M-/M-'
            EQ_Model_data = re.findall(pattern = EQ_regex, string = Equipment)
        
            #remove instances of PID-1234 and AWP from MAWP from found model EQ words
            EQ_model_data_no_PID = list(EQ_Model_data)
            for word in EQ_Model_data:
                original_word = word
                word = str(word)
                if(sub_str('PID', word) == True):
                    EQ_model_data_no_PID.remove(original_word)
                if(sub_str('AWP', word) == True):
                    EQ_model_data_no_PID.remove(original_word)
            EQ_Model_data = EQ_model_data_no_PID
            
            #SCAN all words on PDFs, classify as EQ
            allWords = results['pages'][0]['words']
            EQ_Scan_data = []
            EQ_Scan_conf = []
            EQ_Scan_poly = []
            #word = allWords[146]
            #word = allWords[479]
            for word in allWords: 
                current_word = word['content']
                current_conf = word['confidence']
                current_poly = word['polygon']
                #new regex with NO parentheses
                #EQ_scan_regex = '[A-Z]?\-?\(?[A-Z]{1,2}\-\d{4,5}\)?\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?\(?[A-Z]{1,2}\-\d{4,5}\)?\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d|TK-\d{4}|BL-\d{4}|SE\.\d{2}\.\d{4}|CV-\d{4}|CE-\d{4}|CO-\d{4}|C0-\d{4}|AC-CO-\d{4}|P-CO-\d{4}|CM-\d{4}|CZ-\d{4}\-\d|AC-\d{4}\-\d|CO\.\d{2}\.\d{4}|CM\.\d{2}\.\d{4}|AC-\d{4}|HT\.\d{2}\.\d{4}|CT-\d{4}|CR-\d{4}|EG-\d{4}|EM-\d{4}|FN-\d{4}|FL-\d{4}|F-\d{4}|F-CO-\d{4}|FL\d{2}[.,]\d{4}|FG-\d{4}|FS-\d{4}|GT-\d{4}|GB-\d{4}|HE-\d{4}|HR-\d{4}|HR\d{2}[.,]\d{4}|HB-\d{4}|HTR-\d{4}|H-\d{4}|MX-\d{4}|M-\d{5}|M-/M-\d{4,5}|NO-\d{4}|PI-\d{4}|PT-\d{4}|PV-\d{4}|PR\d{2}[.,]\d{4}|PU-\d{4}|PM[.,]\d{2}[.,]\d{4}|PM\d{2}\.\d{4}|PR-\d{4}|TR-\d{4}|SK-\d{4}|ST-\d{4}|SR-\d{4}|S-\d{4}|SP-\d{4}|WC-\d{4}|CS-\d{4}|SW-\d{4}|TC-\d{4}|DU\.\d{2}\.\d{4}|TE-\d{4}|TU-\d{4}|UP-\d{4}|UCP-\d{4}|UC-\w\d{4}|UC\w?\-[A-Z]{0,2}\-\d{4}|VE-\d{4}|WI-\d{4}|FE-\d{4}|BPV-\d{4}|GC-\d{4}|M-\d{5}|MM-\d{2}|BM-\w{2}\d{4}|F-\d{2}|NG-\d{4}|G-\d{4}|MS-\d{2}|EH-\d{4}|EH-\d{2}|FL-|M-/M-'
        
                #EQ_scan_regex = '[A-Z]?\-?\(?[A-Z]{1,2}\-\d{3,5}\)?\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}\/?\d{0,4}\/?\d{0,4}|[A-Z]?\-?\(?[A-Z]{1,2}\-\d{3,5}\)?\-?\/?\d{0,5}\w?\/?[A-Z]{0,4}\-?\d{0,5}|[A-Z]{2}\d{2}\,?\.?\d{3,4}.?\.?\d{0,4}[A-Z]\/[A-Z]\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]?\/?[A-Z]{0,2}|[A-Z]{2}[,.]?\d{2}[.,]\d{4}|[A-Z]{2}[,.]?\d{2}[.,]\d{3}\.\d|TK-\d{4}|BL-\d{4}|SE\.\d{2}\.\d{4}|CV-\d{4}|CE-\d{4}|CO-\d{4}|C0-\d{4}|AC-CO-\d{4}|P-CO-\d{4}|CM-\d{4}|CZ-\d{4}\-\d|AC-\d{4}\-\d|CO\.\d{2}\.\d{4}|CM\.\d{2}\.\d{4}|AC-\d{4}|HT\.\d{2}\.\d{4}|CT-\d{4}|CR-\d{4}|EG-\d{4}|EM-\d{4}|FN-\d{4}|FL-\d{4}|F-\d{4}|F-CO-\d{4}|FL\d{2}[.,]\d{4}|FG-\d{4}|FS-\d{4}|GT-\d{4}|GB-\d{4}|HE-\d{4}|HR-\d{4}|HR\d{2}[.,]\d{4}|HB-\d{4}|HTR-\d{4}|H-\d{4}|MX-\d{4}|M-\d{5}|M-/M-\d{4,5}|NO-\d{4}|PI-\d{4}|PT-\d{4}|PV-\d{4}|PR\d{2}[.,]\d{4}|PU-\d{4}|PM[.,]\d{2}[.,]\d{4}|PM\d{2}\.\d{4}|PR-\d{4}|TR-\d{4}|SK-\d{4}|ST-\d{4}|SR-\d{4}|S-\d{4}|SP-\d{4}|WC-\d{4}|CS-\d{4}|SW-\d{4}|TC-\d{4}|DU\.\d{2}\.\d{4}|TE-\d{4}|TU-\d{4}|UP-\d{4}|UCP-\d{4}|UC-\w\d{4}|UC\w?\-[A-Z]{0,2}\-\d{4}|VE-\d{4}|WI-\d{4}|FE-\d{4}|BPV-\d{4}|GC-\d{4}|M-\d{5}|MM-\d{2}|BM-\w{2}\d{4}|F-\d{2}|NG-\d{4}|G-\d{4}|MS-\d{2}|EH-\d{4}|EH-\d{2}|FL-|M-/M-'
                #REGEX = pd.read_csv("name_regex_lookup.csv")
                #EQ_regex = REGEX['Equipment Regex Text Only']
                #EQ_Scan_word = re.findall(pattern = '|'.join(EQ_regex), string = current_word)
                EQ_Scan_word = re.findall(pattern = EQ_regex, string = current_word)
                
                if EQ_Scan_word != []:
                    EQ_Scan_data.append(EQ_Scan_word)
                    EQ_Scan_conf.append(current_conf)
                    EQ_Scan_poly.append([EQ_Scan_word,current_poly])
        
            # print("Scan EQs: ")
            # print(EQ_Scan_data)
        
            #remove duplicates in the poly coordinate data
            #cancleing "drop duplicated" to hopefully get audience EQ tags highlighted green
            #EQ_POLY_DF = pd.DataFrame(EQ_Scan_poly, columns = ['Tag', 'Poly'])
            #EQ_POLY_CLEAN = EQ_POLY_DF.drop_duplicates(subset = ['Tag'])
            #EQ_Scan_poly = EQ_POLY_CLEAN.values.tolist()
            
            #remove instances of PPID-1234 and AWP-1234 from scanned EQ tags
            EQ_Scan_data_no_PID = list(EQ_Scan_data)
            for word in EQ_Scan_data:
                original_word = word[0]
                if(sub_str('PID', original_word) == True):
                    EQ_Scan_data_no_PID.remove(word)
                if(sub_str('AWP', original_word) == True):
                    EQ_Scan_data_no_PID.remove(word)
                
            EQ_Scan_data = EQ_Scan_data_no_PID

            #save a full list of EQ tags scanned
            #drop duplicates on this list
            EQ_Scan_full_data = EQ_Scan_data
            #then remove double instances of the repeated EQ's
            EQ_SCAN_FULL_DF = pd.DataFrame(EQ_Scan_full_data)
            EQ_DROP_FULL = EQ_SCAN_FULL_DF.drop_duplicates()
            EQ_Scan_full_data = EQ_DROP_FULL.values.tolist()
            
            if(len(EQ_Scan_full_data) > 1):
                i = 0
                while i < len(EQ_Scan_full_data):
                    EQ_Scan_full_data[i] = EQ_Scan_full_data[i][0]
                    i += 1
            
            # print("EQ Scanned full data (no duplicates, AWP, or PID): ")
            # print(EQ_Scan_full_data)
            
            #keep duplicates, save as EQ OCR data ()
            EQ_SCAN_DF = pd.DataFrame(EQ_Scan_data)
            EQ_SCAN_duplicates = EQ_SCAN_DF[EQ_SCAN_DF.duplicated(keep=False)]
            EQ_Scan_data = EQ_SCAN_duplicates.values.tolist()
        
            #then remove double instances of the repeated EQ's
            EQ_SCAN_DF = pd.DataFrame(EQ_Scan_data)
            EQ_DROP = EQ_SCAN_DF.drop_duplicates()
            EQ_Scan_data = EQ_DROP.values.tolist()
            
            #save the tags as 'strings' not ['strings']
            if(len(EQ_Scan_data) > 1):
                i = 0
                while i < len(EQ_Scan_data):
                    EQ_Scan_data[i] = EQ_Scan_data[i][0]
                    i += 1

            # print("EQ scanned EQ's with cleaning: ")
            # print(EQ_Scan_data)
    
            #ASSIGN polygon corner data to either
            #   GREEN: confirmed equipment tags
            #   YELLOW: possible equipment tags
            green_tags = []
            yellow_tags = []
            #entry = allWords[4]
            #for entry in allWords:
            for entry in EQ_Scan_poly:
                tag = entry[0]
                cord = entry[1]
                if (tag in EQ_Model_data or tag[0] in EQ_Model_data):
                    green_tags.append([tag, cord])
                elif (tag in EQ_Scan_data or tag[0] in EQ_Scan_data):
                    green_tags.append([tag, cord])
                elif (tag in EQ_Scan_full_data or tag[0] in EQ_Scan_full_data):
                    yellow_tags.append([tag, cord])
                    
            #DATA FRAME 2: EQ_FRAME_2   
            green_attribute = []
            yellow_attribute = []
            allLines = results['pages'][0]['lines']
            index = 0
            #index =89
            while(index < len(allLines)):
                current_line = allLines[index]['content']
                
                #MODEL EQ ATTRIBUTES
                #reset the tags found in the current line
                eq_tags = []
                #if this line has an equipment tag in it,
                eq_tags = re.findall(pattern = EQ_regex, string = current_line)
                #eq_tags = ['P-106', 'PU-1020A']
                
                #if the regex found an EQ tag IN the current line,
                if eq_tags != []:
                    #for each tag that it recognized,
                    for tag in eq_tags:
                        #print(tag)
                        #if the tag is one that the model recognized
                        if(tag in EQ_Model_data):
                            #print("in model")
                            
                            #save the EQ tag
                            #tag = current_line
                            attribute_counter = 0
                            #is the next line a valid attribute but not a new equipment tag,
                            while( (allLines[index+1]['content'] in Equipment)and (allLines[index+1]['content'] not in EQ_Model_data)):
                                phrase = allLines[index+1]['content']
                                current_poly = allLines[index+1]['polygon']
                                if(len(phrase) > 1):    #save the attribute
                                    attribute_counter += 1
                                    attribute = "Attribute #" + str(attribute_counter)
                                    EQ_FRAME_2 = EQ_FRAME_2.append({'Equipment Tag': tag, 'Equipment Attribute': attribute, 'Equipment Value': phrase}, ignore_index=True)
                                    green_attribute.append([current_line, phrase, current_poly])
                                index += 1  #check the next line 
                            index += 1
                            
                        #SCANNED EQ ATTRIBUTES
                        #if this is a scanned EQ tag that's seen twice, mark it green
                        elif(tag in EQ_Scan_data):
                            #print("in scan")
                            #save the line following the tag (usually the name of the machine)
                            #tag = current_line
                            phrase = allLines[index+1]['content']
                            current_poly = allLines[index+1]['polygon']
                            if((phrase not in EQ_Scan_data) and (len(phrase) > 5)):  
                                attribute = "Attribute #1"
                                EQ_FRAME_2 = EQ_FRAME_2.append({'Equipment Tag': tag, 'Equipment Attribute': attribute, 'Equipment Value': phrase}, ignore_index=True)
                                green_attribute.append([current_line, phrase, current_poly])
                            index += 1
                        #if this is a scanned EQ tag that's seen ONCE, mark it yellow
                        elif(tag in EQ_Scan_full_data):
                            #print("in full scan")
                            #save the line following the tag (usually the name of the machine)
                            #tag = current_line
                            phrase = allLines[index+1]['content']
                            current_poly = allLines[index+1]['polygon']
                            if((phrase not in EQ_Scan_data) and (len(phrase) > 5)):  
                                attribute = "Attribute #1"
                                EQ_FRAME_2 = EQ_FRAME_2.append({'Equipment Tag': tag, 'Equipment Attribute': attribute, 'Equipment Value': phrase}, ignore_index=True)
                                yellow_attribute.append([current_line, phrase, current_poly])
                            index += 1 
                        else:
                            #line is not an EQ tag, continue to next line
                            index += 1 
                else:
                    index += 1      
    
                
            #EQUIPMENT DATAFRAME 1
            for tag in EQ_Model_data:
                
                abbreviation = tag[:2]
                rows = EQ_NAMES.loc[EQ_NAMES['Equipment_Abbreviation']==abbreviation]
                if( rows.size != 0):
                    type = rows['Equipment_Type_Name'].unique()
                    #type = type[0]
                    type = type[0].replace('\xa0', " ")
                else:
                    type = 'Unknown' 
                EQ_FRAME_1 = EQ_FRAME_1.append({'Drawing Number': Drawing_Number, 'Equipment Type':type, 'Equipment Tag': tag}, ignore_index=True)
            
            for tag in EQ_Scan_data:
                if( tag not in EQ_Model_data): 
                    abbreviation = tag[:2]
                    rows = EQ_NAMES.loc[EQ_NAMES['Equipment_Abbreviation']==abbreviation]
                    if( rows.size != 0):
                        type = rows['Equipment_Type_Name'].unique()
                        type = type[0].replace('\xa0', " ")
                    else:
                        type = 'Unknown'
                    EQ_FRAME_1 = EQ_FRAME_1.append({'Drawing Number': Drawing_Number, 'Equipment Type':type, 'Equipment Tag': tag}, ignore_index=True)
                
        except Exception as e:###

            error_log.append(['Extraction','Equipment',e])   
        
    ## Check if pdf_name is defined
        try:
            pdf_name
        except NameError:
            pdf_name = None
        else:
            pdf_name = pdf_name

    
        ## Create data to return
        report_data = [[Equipment,Equipment_conf,EQ_Model_data,EQ_Scan_conf,Line_Number, Line_conf, Drawing_Number,Drawing_conf]]
        DATA = pd.DataFrame(report_data,columns=['Equipment','Equipment Confidence', 'Equipment Tags', 'Equipment OCR Confidence','Line Number','Line Confidence','Drawing Number','Drawing Confidence'])
        
        ## Create `ERROR LOG`
        ERROR_LOG = pd.DataFrame(error_log,columns=['Location','Field','Description']) ## Create `ERROR_LOG`
        
        #create data to send to make dataframes
        #results = [Drawing_Number, EQ_Model_output, EQ_model_data, EQ_Scan_full_data, EQ_Scan_data, Line_Number]
        #RESULTS = pd.DataFrame( results, columns = ['Drawing Number', 'EQ Model Output', 'EQ Model Tags', 'EQ Scan Output', 'EQ Scan Tags', 'Line Numbers'])

        return(DATA,ERROR_LOG, EQ_FRAME_1, EQ_FRAME_2, LINE_FRAME_1, LINE_FRAME_2, EQ_Scan_full_data, EQ_Scan_data, yellow_tags, green_tags, line_poly, green_attribute, yellow_attribute, draw_poly)
    
    except Exception as e:
        ## Append the general python error to the error log
        error_log.append(['Extract','General python exception',e])
        
        #pass empty lists
        yellow_tags = []
        green_tags= []
        line_poly = []
        green_attribute = []
        
        ## Create ERROR_LOG dataframe
        ERROR_LOG = pd.DataFrame(error_log,columns=['Location','Field','Description'])
        
        ## Create empty MCR dataframe
        DATA = pd.DataFrame(columns=['Equipment','Equipment Confidence','Equipment OCR', 'Equipment OCR Confidence','Line Number','Line Confidence','Drawing Number','Drawing Confidence'])
        #RESULTS = pd.DataFrame(columns = ['Drawing Number', 'EQ Model Output', 'EQ Model Tags', 'EQ Scan Output', 'EQ Scan Tags', 'Line Numbers'])
        
        return(DATA,ERROR_LOG, EQ_FRAME_1, EQ_FRAME_2, LINE_FRAME_1, LINE_FRAME_2, EQ_Scan_full_data, EQ_Scan_data, yellow_tags, green_tags, line_poly, green_attribute, yellow_attribute, draw_poly)
   
#initialize empty dataframes
EQ_FRAME_1 = pd.DataFrame()
EQ_FRAME_2 = pd.DataFrame()
LINE_FRAME_1 = pd.DataFrame()
LINE_FRAME_2 = pd.DataFrame()                                                       

## Extract report data
EXTRACT_RESULTS,EXTRACT_ERRORS, EQ_FRAME_1, EQ_FRAME_2, LINE_FRAME_1, LINE_FRAME_2,  EQ_scan_full_tags, EQ_scan_cleaned_tags, yellow_tags, green_tags, line_poly, green_attribute, yellow_attribute, draw_poly = general_extract(results=results,
                                                       pdf_name=pdf_name,
                                                       EQ_FRAME_1 = EQ_FRAME_1,
                                                       EQ_FRAME_2 = EQ_FRAME_2,
                                                       LINE_FRAME_1 = LINE_FRAME_1,
                                                       LINE_FRAME_2 = LINE_FRAME_2,
                                                       EQ_NAMES = EQ_NAMES
)

 

    
def highlight(pid_pdf, results, green_tags, yellow_tags, green_attribute, line_poly, draw_poly):

    # Define Input PDF 
    inputFile = pid_pdf

    # Define Output Highlighted PDF file name
    pid_pdf_str = pid_pdf.replace('.pdf', "")
    outputFile = str(pid_pdf_str) + "_HL.pdf"
    
    #if the highlighted PDF already exists, delete it
    if(os.path.exists(outputFile)):
        os.remove(outputFile)
    
    # Define Output Writer
    writer = PdfFileWriter()

    # Define the original inputted PDF (no highlights)
    inputPDF = PdfFileReader(open(inputFile, "rb"))
    input = inputPDF.getPage(0)
    #input = PdfFileReader(open(inputFile, "rb")).getPage(0)

    # Get Dimensions and Information from this original PDF
    input_height = float(input.mediabox.getHeight())
    input_width = float(input.mediabox.getWidth())
    rotated = int(input['/Rotate'])
    
    #define the height and width of the page in inches (instead of points)
    input_height_inch = input_height/72
    input_width_inch = input_width/72
 
    # Define Colors for Highlighting
    red50Transparent = Color(100, 0, 0, alpha=0.5)
    green50Transparent = Color(0, 100, 0, alpha=0.5)
    purple50Transparent = Color(0, 0, 100, alpha=0.5)
    blue50Transparent = Color(0, 80, 100, alpha=0.5)
    yellow50Transparent = Color(20, 100, 0, alpha=0.5)

    # Define Packet and Canvas Size
    packet = io.BytesIO()
    can = Canvas(packet, pagesize=(input_width, input_height))


    #VERTICAL ENTRY NOTATIONS =============================================================

    if(rotated == 270):
        #print("rotated 270")
        #like PID PDF page 32
        #the original PDF is read in automatically rotated,
        #so the original PDF is a vertical, upside down P&ID
        
        
        #process includes some coordinate transformations
        #PYPDF maps all y coordinates backwards (bottom to top) instead of (top to bottom)
        #so any coordinate that ends up as a "y" for pyPDF has to be subtracted from the
        #originl height or width(depending on which)
        
        #rectangles are highlighted with the arguments [lowest x, lowest y, width of rect, height of rect]
        #from each polygon data set,
        #v: vertical
        #v_low x = width - high y polygon
        #v_high_x = width - low y polygon
        #v_low_y = height - high x polygon
        #v_high_y = height - low x polygon
        
        #v_width = (width - low y poly) - (width - high y poly)
        #v_height = (height - lowest x poly) - (height - high x poly)
        
        #reference code and structure from perfectly horizontal coordinates:
        #   if green_tags != []:
        #     for entry in green_tags:
        #         word = entry[0][0]
        #         lowest_x = entry[1][0]['x']
        #         high_y = input_height_inch - entry[1][1]['y']
        #         highest_x = entry[1][2]['x']
        #         low_y = input_height_inch - entry[1][3]['y']
                
        #         r_width = highest_x - lowest_x
        #         r_height = high_y - low_y
                # greenWords.append([word, lowest_x, low_y, r_width, r_height])
        
        #intialize green highlight list
        greenWords = []
        
        if green_tags != []:
            for entry in green_tags:
                word = entry[0][0]
                v_low_x = input_width_inch - entry[1][3]['y']
                v_high_x = input_width_inch - entry[1][1]['y']
                v_low_y = input_height_inch - entry[1][2]['x']
                v_high_y = input_height_inch - entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                greenWords.append([word,v_low_x, v_low_y, v_width, v_height])

            
        if green_attribute != []:
            for entry in green_attribute:
                word = entry[1]
                v_low_x = input_width_inch - entry[2][3]['y']
                v_high_x = input_width_inch - entry[2][1]['y']
                v_low_y = input_height_inch - entry[2][2]['x']
                v_high_y = input_height_inch - entry[2][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                greenWords.append([word,v_low_x, v_low_y, v_width, v_height])
                
        #initialize yellow highlight list
        yellowWords = []
        if yellow_tags != []:
            for entry in yellow_tags:
                word = entry[0][0]
                v_low_x = input_width_inch - entry[1][3]['y']
                v_high_x = input_width_inch - entry[1][1]['y']
                v_low_y = input_height_inch - entry[1][2]['x']
                v_high_y = input_height_inch - entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                yellowWords.append([word,v_low_x, v_low_y, v_width, v_height])

        redWords = []
        if(line_poly != []):
            for entry in line_poly:
                word = entry[0]
                v_low_x = input_width_inch - entry[1][3]['y']
                v_high_x = input_width_inch - entry[1][1]['y']
                v_low_y = input_height_inch - entry[1][2]['x']
                v_high_y = input_height_inch - entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                redWords.append([word,v_low_x, v_low_y, v_width, v_height])
                
        #drawing number highlighted in a different color
        blueWords = []
        entry = draw_poly

        v_low_x = input_width_inch - entry[3]['y']
        v_high_x = input_width_inch - entry[1]['y']
        v_low_y = input_height_inch - entry[2]['x']
        v_high_y = input_height_inch - entry[0]['x']
        
        v_width = v_high_x - v_low_x
        v_height = v_high_y - v_low_y
        blueWords.append([v_low_x, v_low_y, v_width, v_height])

                  
    #90 degree read in (basically horizontal, more similar code from original versions of this)
    if(rotated == 90):
        #similar to PID 8 page 40
        #assumes that the PDF is automatically rotated to be horizontal
        #print("rotated = 90")
                
        #intialize green highlight list
        greenWords = []
        
        if green_tags != []:
            for entry in green_tags:
                word = entry[0][0]
                v_low_x = entry[1][3]['y']
                v_high_x = entry[1][1]['y']
                v_low_y = entry[1][2]['x']
                v_high_y = entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                greenWords.append([word,v_low_x, v_low_y, v_width, v_height])
    
            
        if green_attribute != []:
            for entry in green_attribute:
                word = entry[1]
                v_low_x = entry[2][3]['y']
                v_high_x = entry[2][1]['y']
                v_low_y =  entry[2][2]['x']
                v_high_y = entry[2][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                greenWords.append([word,v_low_x, v_low_y, v_width, v_height])
                
        yellowWords = []
        if yellow_tags != []:
            for entry in yellow_tags:
                word = entry[0][0]
                v_low_x =  entry[1][3]['y']
                v_high_x = entry[1][1]['y']
                v_low_y =  entry[1][2]['x']
                v_high_y =  entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                yellowWords.append([word,v_low_x, v_low_y, v_width, v_height])

        redWords = []
        if(line_poly != []):
            for entry in line_poly:
                word = entry[0]
                v_low_x =  entry[1][3]['y']
                v_high_x =  entry[1][1]['y']
                v_low_y =  entry[1][2]['x']
                v_high_y =  entry[1][0]['x']
                
                v_width = v_high_x - v_low_x
                v_height = v_high_y - v_low_y
                redWords.append([word,v_low_x, v_low_y, v_width, v_height])
                
        blueWords = []
        entry = draw_poly

        v_low_x = entry[3]['y']
        v_high_x = entry[1]['y']
        v_low_y = entry[2]['x']
        v_high_y = entry[0]['x']
        
        v_width = v_high_x - v_low_x
        v_height = v_high_y - v_low_y
        blueWords.append([v_low_x, v_low_y, v_width, v_height])
        
    
    #OVERLAY HIGHLIGHT=================================================================================
    # Create DFs
    # Define Canvas Highlighting
    
    if greenWords:
        greenWordsDF = pd.DataFrame(greenWords)
        greenWordsDF.columns = ['Word', 'x1', 'y1', 'width', 'height']
        can.setFillColor(green50Transparent)
        for i in range(len(greenWordsDF)):
            can.rect(greenWordsDF['x1'].iloc[i]*inch, greenWordsDF['y1'].iloc[i]*inch, greenWordsDF['width'].iloc[i]*inch, greenWordsDF['height'].iloc[i]*inch, fill=True, stroke=False)
        
    if yellowWords:
        yellowWordsDF = pd.DataFrame(yellowWords)
        yellowWordsDF.columns = ['Word', 'x1', 'y1', 'width', 'height']
        
        can.setFillColor(yellow50Transparent)
        for i in range(len(yellowWordsDF)):
            can.rect(yellowWordsDF['x1'].iloc[i]*inch, yellowWordsDF['y1'].iloc[i]*inch, yellowWordsDF['width'].iloc[i]*inch, yellowWordsDF['height'].iloc[i]*inch, fill=True, stroke=False)
        
    if redWords:
        redWordsDF = pd.DataFrame(redWords)
        redWordsDF.columns = ['Word', 'x1', 'y1', 'width', 'height']
        can.setFillColor(red50Transparent)
        for i in range(len(redWordsDF)):
            can.rect(redWordsDF['x1'].iloc[i]*inch, redWordsDF['y1'].iloc[i]*inch, redWordsDF['width'].iloc[i]*inch, redWordsDF['height'].iloc[i]*inch, fill=True, stroke=False)
    
    if blueWords:
        blueWordsDF = pd.DataFrame(blueWords)
        blueWordsDF.columns = ['x1', 'y1', 'width', 'height']
        can.setFillColor(blue50Transparent)
        can.rect(blueWordsDF['x1'][0]*inch, blueWordsDF['y1'][0]*inch, blueWordsDF['width'][0]*inch, blueWordsDF['height'][0]*inch, fill=True, stroke=False)
    
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

    return 1


#see highlights visualized on the PDFs
#saves new PDF called pid_pdf_HL.pdf
done = highlight(pid_pdf, results, green_tags, yellow_tags, green_attribute, line_poly, draw_poly)

