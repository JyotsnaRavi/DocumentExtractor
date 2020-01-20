# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 08:18:45 2020

@author: jyravi
"""
#%%%
from ImageDocumentExtractorV2 import ImageDocumentExtractor


#%%%


#newpath="C:\\Users\\jyravi\\OCRPython\\\scannedPdf\\ScannedSOW.pdf"


#newpath=r"C:\Users\jyravi\OCRPython\zdocuments\completetextextraction3\LOE_Light_359831.pdf"

newpath=r"C:\Users\jyravi\OCRPython\zdocuments\completetextextraction4\LOE.pdf"

#newpath=r"C:\Users\jyravi\OCRPython\InfosysPoC\completetextextraction6\TEBI20TZ.pdf"


#%%
vision_base_url="https://southeastasia.api.cognitive.microsoft.com/vision/v2.1/"
endpoint = vision_base_url + "read/core/asyncBatchAnalyze"

key=""

mode="Printed"
#%%
imgextract=ImageDocumentExtractor(endpoint,key,mode)   
       
#%%
dim,zippedtext,textsummarized=imgextract.textExtraction(newpath)

#%%
textextracted,tabularSinglevaluepre,headers_extracted=imgextract.crackedelements(zippedtext,dim,"pdf")

#%%%
keyValues,table_list=imgextract.keyvalueTable(tabularSinglevaluepre)

#%%

####### Just a test to put it to tables based on the index value ######################################
df_list=table_list
newextracted_tables={}
newid=1
for iii in df_list:
    inde=df_list.index(iii)
    rangeindex=range(iii[0],iii[0]+4)
    rangenindex=range(iii[0],iii[0]+4)
    
    try:
        if (df_list[inde+1][0] in rangenindex and df_list[inde+1][1]==df_list[inde][1]):
            
            if newid not in newextracted_tables.keys():
                newextracted_tables[newid]=[]
                newextracted_tables[newid].append(iii[2:])
                newextracted_tables[newid].append(df_list[inde+1][2:])
            else:
                newextracted_tables[newid].append(df_list[inde+1][2:]) 
        elif(df_list[inde+1][0] in rangeindex and df_list[inde+1][1]!=df_list[inde][1]):
            if newid not in newextracted_tables.keys():
                newextracted_tables[newid]=[]
                
                
                newextracted_tables[newid].append(iii[2:])
                newextracted_tables[newid].append(df_list[inde+1][2:])
            else:
                newextracted_tables[newid].append(df_list[inde+1][2:]) 
        else:
            newid=newid+1
            if newid not in newextracted_tables.keys():
                newextracted_tables[newid]=[]
                newextracted_tables[newid].append(df_list[inde+1][2:])
            else:
                newextracted_tables[newid].append(df_list[inde+1][2:])
    except:
        print("exiting the loop")
#%%
