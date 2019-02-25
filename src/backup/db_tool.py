# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 12:16:42 2018

@author: 683898
"""
from os import listdir, makedirs
from os.path import exists,isfile,join
from configparser import ConfigParser
import sys
import utility as ut
import vision_tool as vt

if __name__ == '__main__':
    try:
        configFile = ConfigParser()
        configFile.read(ut.API_CONFIG_FILE)
        
        #Google cloude vision API Related Parameter
        ENDPOINT_URL = configFile.get('COMMONPARAMS','url')
        API_KEY= configFile.get('COMMONPARAMS','key')
        TYPE = configFile.get('COMMONPARAMS','type')
        
        #input image output DOC and Json Paths
        IMAGE_DIR = configFile.get('DB.Paths','inputimagepath')
        DB_DIR = configFile.get('DB.Paths','dbdocpath')
        JSON_DIR = configFile.get('DB.Paths','jsonpath')

        #TYpe of DOC and Other DEFAULT parameters
        MAKE_JSON = configFile.getboolean('DB.DEFAULT','makejson')
        DOC_TYPE = configFile.get('DB.DEFAULT','DB_DOC_TYPE')
    except ConfigParser.ParsingError as e:
        sys.exit(e)
    except Exception as e:    
        sys.exit(e)
    else:
        print('CONFIG FILE LOADED SUCESSFULLY ')
        makedirs(JSON_DIR, exist_ok=True)
        makedirs(DB_DIR, exist_ok=True)
    finally:
        pass
    
    #Validating API_KEY and ENDPOINT_URL     
    if not API_KEY or not ENDPOINT_URL:
       sys.exit("API_KEY or ENDPOINT_URL is invalid")
    if not exists(IMAGE_DIR) :
        sys.exit("IMAGE_DIR is invalid")
    else:
        IMAGE_FILENAMES=[ join(IMAGE_DIR,file) for file in listdir(IMAGE_DIR) 
                          if isfile(join(IMAGE_DIR, file))]
        
    #Displaying Parameters 
    print("URL :{} , KEY :{}".format(ENDPOINT_URL,API_KEY))
    print(IMAGE_FILENAMES)
    
    # calling vision api
    try:
        visionApi = vt.VisionApi(ENDPOINT_URL,API_KEY,TYPE)
        response =  visionApi.request_ocr(IMAGE_FILENAMES)  
    except Exception as e:
        sys.exit(e)        
    else:
        if ( response.status_code != 200 or response.json().get('error')):
           print("NOT RETURN ANY RESPONSE FROM GCV")  
           #print(response.text)    
        else:
           text_response=visionApi.process_response(MAKE_JSON,JSON_DIR,
                                                    response,IMAGE_FILENAMES)
           #vt.visionApi.write_ResponseJson(JSON_DIR,response,IMAGE_FILENAMES)
           visionApi.write_ResponseJson(JSON_DIR,response,IMAGE_FILENAMES)
           visionApi.write_textonly(DB_DIR,response,IMAGE_FILENAMES,DOC_TYPE)
           #vt.visionApi.capture_output(text_response,IMAGE_DIR,JSON_DIR)
    finally:
        print("EXITING FROM CODE")