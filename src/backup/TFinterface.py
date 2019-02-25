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
import GoogleOcr as ocr
import utility as ut
from  processCSV import csv2Box 
import json

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
            raise Exception
        #img = cv2.imread(ImagePath)
        #height, width, channels = img.shape
        height, width=2988,5312
        OCR=ocr.GCVOCR(ENDPOINT_URL,API_KEY,TYPE,JSON_DIR,IMAGE_DIR)
        OCR.ExtractText(boxInfo,height, width)
        imgname = basename(boxInfo["File"]).split(".")[0]
        jpath = join(JSON_DIR,imgname+'Amended.json')                             
        with open(jpath, 'w') as f:
             datatxt = json.dumps(boxInfo, indent=2)
             print("Wrote", len(datatxt), "bytes to", jpath)
             f.write(datatxt) 
             
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
        ENDPOINT_URL = configFile.get('URLPARAMS','url')
        API_KEY= configFile.get('URLPARAMS','key')
        TYPE = configFile.get('URLPARAMS','type')
        if not API_KEY or not ENDPOINT_URL:
           sys.exit('API_KEY:{} or ENDPOINT_URL:{} is invalid'.format(API_KEY,ENDPOINT_URL))
        JSON_DIR = configFile.get('Paths','jsonpath')
        makedirs(JSON_DIR, exist_ok=True)           
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