# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 01:19:28 2018

@author: 683898
"""
import os
import sys
from configparser import ConfigParser

config=ConfigParser() 

config['Paths']={
        'Project_Home_Dir': 'D:\\OCR',
        'ImagePath'       : 'D:\\OCR\\Inputs\\50Test_distinct_scn',
        'TFCSVFile'       : 'D:\\OCR\\Inputs\\Tfcsv\\Deo.csv',
        'DBDOCPath'       : 'D:\\OCR\\database\\CRAFTED_DOC',
        'JsonPath'        : 'D:\\OCR\\Output\\Json',
        'DBIMAGEPATH'     : 'D:\\OCR\\database\\Images\\Deo',
        'TEMPDIR'         : 'D:\\Python\\GCV\\test_output'}

config['DEFAULT']={
        'Mode'       : 'Release',
        'MakeJson'   :  False,
        'DB_DOC_TYPE': 'json',
        'IMAGETYPE'  : ['jpg','JPEG','JPG','png','PNG']}

config['OCRPARAM']={
        'Url'      : 'https://vision.googleapis.com/v1/images:annotate',
        'key'      : 'AIzaSyBExERfhOOk5qScBGSfJsl6ummuPpKCJLo',
        'BatchSize': '10',
        'Type'     : 'DOCUMENT_TEXT_DETECTION'}

config['SOLRPARAM']={
        'HOSTID'          : '198.162.0.103',
        'PORT'            :  8983,
        'SPELLCHECK_CORE' : 'DEO',
        'QUERY_CORE'      : 'DEOProduct',
        'REMOTE_HOST'     :  False
        }

config['PROXYPARAM']={
        'ENABLE_PROXY'    :  True,    
        'HTTPS_PROXY'     :  'http://683898:Paramita@20@proxy.tcs.com:8080',
        'HTTP_PROXY'      :  'http://683898:Paramita@20@proxy.tcs.com:8080',
        }


configFileName='./config.ini'

try :
    if (os.path.exists(configFileName)):
        print(" Amending Existing Config File")
        with open (configFileName,'w') as configFile:
             config.write(configFile)
    else:
        print(" Writing Fresh Config File")
        with open (configFileName,'w') as configFile:
             config.write(configFile)
except Exception as e:
    sys.exit(e)
else :
    print(" Config File Sucessfully created")
finally:
    pass