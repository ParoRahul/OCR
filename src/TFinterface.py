# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 13:15:00 2018

@author: 683898
"""
from os import listdir, makedirs
from os.path import exists,isfile,join,basename
import sys
import cv2
from configparser import ConfigParser
import json
import GoogleOcr as ocr
import utility as ut
from  processCSV import csv2Box 
from solrConnection import solr


def update_Corner(tfDict_list):
    try:
        for ImgInfo in tfDict_list:
            update_BoxCorner(ImgInfo)
    except Exception as e:
        print(e)
        raise


def update_BoxCorner(ImgInfo):
    try:
        ImagePath=join(IMAGE_DIR,ImgInfo["File"])
        if (not exists(ImagePath)):
            return None
        img = cv2.imread(ImagePath)
        height, width, channels = img.shape
        ratio_w=float(width)/float(ImgInfo['width'])
        ratio_h=float(height)/float(ImgInfo['height'])
        for Box in ImgInfo["boxlist"]:
            xmin,ymin=Box['box'][0][0]*ratio_w,Box['box'][0][1]*ratio_h
            xmax,ymax=Box['box'][1][0]*ratio_w,Box['box'][1][1]*ratio_h
            Box['box'][0][0]=xmin
            Box['box'][0][1]=ymin
            Box['box'][1][0]=xmax
            Box['box'][1][1]=ymax
    except Exception as e:
        print(e)
        raise
                
def ProcessSingleFile(boxInfo):    
    """ """
    try:
        ImagePath=join(IMAGE_DIR,boxInfo["File"])
        if (not exists(ImagePath)):
            raise Exception("File :{} Not Found ".format(ImagePath))
        img = cv2.imread(ImagePath)
        height, width, channels = img.shape
        #height, width=2988,5312
        boxInfo['OWIDTH']=width
        boxInfo['OHEIGHT']=height
        OCR=ocr.GCVOCR(ENDPOINT_URL,API_KEY,TYPE,JSON_DIR,IMAGE_DIR)
        OCR.ExtractText(boxInfo,height,width)
        textMatcher=solr(SOLR_HOSTID,SOLR_PORT,SOLR_CORE2)
        #predict_list=[]
        #copyInFo=boxInfo['boxlist'].copy()
        for id,box in enumerate(boxInfo['boxlist']):            
            if (box["LEVEL"]==-1):
                box["OCRPREDICTION"]=str(box['LEVEL'])
                box["REMARK"]="INVALID BOX COPY OLD LEVEL"
                continue
            print(box["TEXT"])
            levellist=textMatcher.request_ORQuery(box["TEXT"])
            if levellist:
               if box['LEVEL'] in levellist:
                  box["OCRPREDICTION"]=str(box['LEVEL'])
                  box["REMARK"]=str(levellist)+" COPY OLD LEVEL"
               else:   
                  box["OCRPREDICTION"]=str(levellist[0])
                  box["REMARK"]=str(levellist)+" OCR PREDICT"
               #print(box["OCRPREDICTION"])
            elif levellist is None:
               box["OCRPREDICTION"]=str(box['LEVEL']) 
               box["REMARK"]="OCR RETURN NONE COPY OLD LEVEL"
            else:
               box["OCRPREDICTION"]=str(box['LEVEL']) 
               box["REMARK"]="OCR RETURN EMPTY LIST COPY OLD LEVEL"
        imgname = basename(boxInfo["File"]).split(".")[0]            
        jpath = join(JSON_DIR,imgname+'Amended.json')                             
        with open(jpath, 'w') as f:
             datatxt = json.dumps(boxInfo, indent=2)
             print("Wrote", len(datatxt), "bytes to", jpath)
             f.write(datatxt)    
        ut.DrawOCRDATA(ImagePath,boxInfo)     
    except Exception as e:
        print(e)

def ProcessTFoutputs():
    try:
        configFile = ConfigParser()
        configFile.read(ut.API_CONFIG_FILE)
        print('CONFIG FILE LOADED SUCESSFULLY')
        global IMAGETYPE,IMAGE_FILENAMES,ENDPOINT_URL,API_KEY,TYPE
        global JSON_DIR,IMAGE_DIR                        
        TfCsvFile=configFile.get('Paths','tfcsvfile')
        if (not exists(TfCsvFile)) :
            sys.exit('tfcsvfile:{} File is Not Found '.format(TfCsvFile))
        CSV2BOX=csv2Box(TfCsvFile)
        CSV2BOX.loadcsv()
        print("Total Number of File to be processed  :" , len(CSV2BOX.tfDict_list))
        #Loading InputImages For OCR Extraction
        IMAGE_DIR = configFile.get('Paths','imagepath')
        IMAGETYPE = configFile.get('DEFAULT','IMAGETYPE')
        if (not exists(IMAGE_DIR))   :
            sys.exit('IMAGE_DIR :{} is invalid'.format(IMAGE_DIR))
        else:
            IMAGE_FILENAMES=[ file for file in listdir(IMAGE_DIR) 
                              if isfile(join(IMAGE_DIR, file)) and file.split('.')[1] in IMAGETYPE ]        
        print('Total number of Image File Found in {} is {}'.format(IMAGE_DIR,len(IMAGE_FILENAMES)))    
        #Google cloude vision API Related Parameter
        ENDPOINT_URL = configFile.get('OCRPARAM','url')
        API_KEY= configFile.get('OCRPARAM','key')
        TYPE = configFile.get('OCRPARAM','type')
        if not API_KEY or not ENDPOINT_URL:
           sys.exit('API_KEY:{} or ENDPOINT_URL:{} is invalid'.format(API_KEY,ENDPOINT_URL))
        JSON_DIR = configFile.get('Paths','jsonpath')
        makedirs(JSON_DIR, exist_ok=True)   
        global SOLR_HOSTID,SOLR_PORT,SOLR_CORE1,SOLR_CORE2,SOLR_REMOTE_HOST
        SOLR_HOSTID=configFile.get('SOLRPARAM','hostid')
        SOLR_PORT=configFile.get('SOLRPARAM','port')
        SOLR_CORE1=configFile.get('SOLRPARAM','spellcheck_core')
        SOLR_CORE2=configFile.get('SOLRPARAM','query_core') 
        SOLR_REMOTE_HOST=configFile.get('SOLRPARAM','remote_host')        
        #Iterating Through Python Dict List & processing each file
        for boxInfo in CSV2BOX.tfDict_list :
            if boxInfo['File'] not in IMAGE_FILENAMES:
               print('{} present in CSV file but not Present in {}'.format(boxInfo['File'],IMAGE_DIR)) 
               continue
            print ('processing image {}'.format (boxInfo['File']))
            ProcessSingleFile(boxInfo)
    except ConfigParser.ParsingError as e:
        sys.exit(e)
    except Exception as e:    
        sys.exit(e)
    finally:
        pass    
       
# END of PROCESSTFOUTPUTS

if __name__ == '__main__':
   ProcessTFoutputs()        