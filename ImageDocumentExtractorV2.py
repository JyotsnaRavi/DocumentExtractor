# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 12:42:20 2019

@author: jyravi
"""


from PIL import Image
import string 
import re 
import itertools
from nltk.corpus import stopwords
import time
import requests


class ImageDocumentExtractor(object):
    def __init__(self,endpoint,cogservicekey,operationmode):
        self.endpoint=endpoint
        self.key=cogservicekey
        self.mode=operationmode
    def imagepath(self,imagepath):
        impath=[imagepath]
        return impath
    
    def credentials(self):
        visionurl=self.endpoint
        headers  = {'Ocp-Apim-Subscription-Key': self.key,
                    "Content-Type": "application/octet-stream"}
        #params   = {'handwriting' : True}
        params   = {'mode' : self.mode}
        return visionurl, headers,params
        
   
    def pass2Read(self, img_array):
        with open(img_array, "rb") as image_stream:
        
            data=image_stream.read()
        visionurl,headers,params=self.credentials()
        response = requests.post(visionurl, headers=headers, params=params, data=data)
        response.raise_for_status()
        image_analysis = {}
        while not "recognitionResults" in image_analysis:
            response_final = requests.get(response.headers["Operation-Location"], headers=headers)
            image_analysis = response_final.json()
            time.sleep(2)
        return image_analysis  

        
    def textExtraction(self,pdfpath):
        zippedtextcombined={}
        textsummarized=[]
        poly=self.pass2Read(pdfpath)
        dimen=[[i["width"],i["height"]] for i in poly["recognitionResults"]]
        result_data1=[i["lines"] for i in poly["recognitionResults"]]
        for i in range(len(result_data1)):
            zippedtextcombined[i]=[]
            result_data=list(itertools.chain(result_data1[i]))
            for ii in result_data:
    
                zippedtextcombined[i].append([ii['boundingBox'][0],ii['boundingBox'][1],ii['boundingBox'][2],ii['text'],i+1])
                textstring='.'.join([txt[3] for txt in zippedtextcombined[i]])
                textsummarized.append(textstring)
        zippedtext=list(itertools.chain.from_iterable(zippedtextcombined.values()))
        if pdfpath.endswith(".pdf"):
            dim=dimen[0] 
        else:
            im = Image.open(pdfpath)
            dim = im.size 
        return dim,zippedtext,textsummarized
    
    def preProcess(self,text):
        data=re.sub(r'\d+','',text[0])
        data = re.compile('[%s]' % re.escape(string.punctuation)).sub('',data)
        Add_op=['thanks','thank you','please','directly','may','behalf','bank','include','inquiries','hope','rode','information','morning','evening','afternoon','amount','total','contact','available']
        stopwrd = set(stopwords.words('english'))
        stopwrd.update(Add_op)  
        textstr=' '.join([i for i in data.split() if i.lower() not in stopwrd])
        return textstr        
        
    def crackedelements(self,zippedtext,dim,filetype):
        textextracted={} 
        #tabularSinglevalue=[]
        textextracted['singleSentence']=[]
        idd=0
        headers_extracted={}
        headers_extracted['headers']=[]
        temporary=[]
        tabularSinglevaluepre=[]
        
        try:
            
            for i in zippedtext:
                ind=zippedtext.index(i)
                if filetype =="img":
                    if dim[0]<=600:
                        r=5
                        cutoff=dim[0]/1.5
                    else:
                        r=10
                        cutoff=dim[0]/3 
                else:
                    r=0.1
                    cutoff=dim[0]/3.5
                if (abs(zippedtext[ind][2]-zippedtext[ind][0]) >= cutoff):
                    p=re.compile('[:;|=]+')
                    firstsplit=p.split(zippedtext[ind][3])
                    if len(firstsplit)==1 or firstsplit[1]=='':               
                        idd=idd+1
                        textextracted['singleSentence'].append(zippedtext[ind][3])
                    else:
                        idd=idd+1
                        tabularSinglevaluepre.append([idd,zippedtext[ind][4],zippedtext[ind][0:3]+[firstsplit[0]],zippedtext[ind][0:3]+[firstsplit[1]]])
                        temporary.append([idd, zippedtext[ind][0:4]])
                elif(abs(zippedtext[ind][1]-zippedtext[ind+1][1])<=r):
                    if tabularSinglevaluepre:
                        if (zippedtext[ind][0:4] != tabularSinglevaluepre[-1][-1]):
                            idd=idd+1
                            tabularSinglevaluepre.append([idd,zippedtext[ind][4],zippedtext[ind][0:4],zippedtext[ind+1][0:4]])
                        else:
                            tabularSinglevaluepre[-1].append(zippedtext[ind+1][0:4])
                    else:
                        tabularSinglevaluepre.append([idd,zippedtext[ind][4],zippedtext[ind][0:4],zippedtext[ind+1][0:4]]) 
                else:
                    unlistedtabularSinglevaluepre=list(itertools.chain.from_iterable([iii[2:] for iii in tabularSinglevaluepre]))
                    textunlistedtabularSinglevaluepre=[i[3] for i in unlistedtabularSinglevaluepre]
                    if  zippedtext[ind][3] not in textunlistedtabularSinglevaluepre:                    
                        headers_extracted['headers'].append([idd,zippedtext[ind][3]])
                        idd=idd+1
        except:
            print("exiting loop")
        finally:
            return textextracted,tabularSinglevaluepre,headers_extracted

    
    def keyvalueTable(self,tabularSinglevaluepre):
        def Sort(sub_li, num1): 
            return(sorted(sub_li, key = lambda x: x[num1]))  
        tabularSinglevalue=[]
        keyValues={}
        table_list=[]
        for each in tabularSinglevaluepre:
            sortedpp=Sort(each[2:],0)
            sortedtext=[ii[3] for ii in sortedpp]
            tabularSinglevalue.append([each[0],each[1],tuple(sortedtext)])
        aa=iter(tabularSinglevalue)
        for eachlist in aa:
            print(len(eachlist))
            if len(eachlist[2])==2:
                print(eachlist[2])
                for ii in eachlist[2]:
                    splitted=re.split(';|:|=|\n',ii)
                    if len(splitted)==2 and splitted[1]!='':
                        if (splitted[0] not in keyValues.keys()):
                            keyValues[splitted[0]]=[]
                            keyValues[splitted[0]].append(splitted[1])
                        else:
                            keyValues[splitted[0]].append(splitted[1])
                    else:
                        if  eachlist[2][0] not in keyValues.keys():
                            keyValues[eachlist[2][0]]=[]
                            keyValues[eachlist[2][0]].append(eachlist[2][1])
            else:
                table_list.append(tuple(eachlist))
        return keyValues,table_list
    

                

            
            
            
            
        
    