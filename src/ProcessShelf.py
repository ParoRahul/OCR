# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 01:24:03 2018

@author: 683898
"""
from os import makedirs,environ
from os.path import exists,join
import sys
from configparser import ConfigParser
import json
#import json
#import requests
import utility as ut
import cv2
import vision_tool as vt
import interface as If

class shelfProcessing(vt.VisionApi):
    
    def __init__(self,ENDPOINT_URL,API_KEY,TYPE,IMAGE_FILENAME,ANNOTATION):        
        vt.VisionApi.__init__(self,ENDPOINT_URL,API_KEY,TYPE)
        self.IMAGE_FILENAME=IMAGE_FILENAME
        self.ANNOTATION=ANNOTATION
        
        
    def DrawLeveledBoxes(self,TEMP_DIR):
        try:
            print(self.IMAGE_FILENAME,TEMP_DIR)
            im = cv2.imread(self.IMAGE_FILENAME[0])
            filename=self.ANNOTATION['File']
            ratio_w=float(2914)/float(self.ANNOTATION['width'])
            ratio_h=float(2404)/float(self.ANNOTATION['height'])
            print(filename)
            nameList=[]
            for box in self.ANNOTATION['boxlist']:
                level=str(box['TEXT'])
                c1 = (int((box['box'][0][0]+box['box'][1][0])*ratio_w/2.0),int((box['box'][0][1]+box['box'][1][1])*ratio_h/2.0))
                cv2.putText(im,level,c1,cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,0,0))
            cropimagename=join(TEMP_DIR,filename.split('.')[0]+'_'+'AnnoTation'+'.'+filename.split('.')[1])
            print(cropimagename)
            #cropimage=im[box['box'][0][1]:box['box'][1][1],box['box'][0][0]:box['box'][1][0]]
            cv2.imwrite(cropimagename,im)
        except KeyError as e:
            raise    
        except Exception as e:
            raise
        else:
            return nameList
            print(" DrawLeveledBoxes Processing Done")
        
        
    def ExtractText(self,ANNOTATION):
        try:
            response=vt.VisionApi.request_ocr(self,IMAGE_LIST)
            if ( response.status_code != 200 or response.json().get('error')):
                 print("NOT RETURN ANY RESPONSE FROM GCV") 
                 raise KeyError
            #vt.VisionApi.write_ResponseJson(self,JSON_DIR,response,IMAGE_LIST)
            print(" GOOGLE OCR RUN ON IMAGE SUCESSFULLY")
            TextSection=response.json()['responses'][0]['textAnnotations']
            for blocknum,block in enumerate(TextSection):
                if blocknum==0:
                    continue
                text=block['description']
                print(text)
                corners=block['boundingPoly']['vertices']
                #topLeft=(twoPoints[0]['x'],twoPoints[0]['y'])
                #bottomRight=(twoPoints[3]['x'],twoPoints[3]['y'])
                index = self.SearchBox(corners)
                if index is None:
                   print ("INDEX NOT FOUND "+str(corners)) 
                   continue
                #print ("INDEX FOUND "+ str(index))                
                text=self.ANNOTATION['boxlist'][index]['TEXT']+text+" "
                self.ANNOTATION['boxlist'][index]['TEXT'] = text
            print(" HI ITERATION DONE ")
            Textonly=json.dumps(self.ANNOTATION,indent=2)
            f = open("importent.json","w")
            f.write(Textonly)
            f.close()            
        except KeyError as e:
            print(e)
            raise    
        except Exception as e:
            print(e)
            raise
        else:
            print(" Shelf Processing Done")
            
    def SearchBox(self,corners):        
        try:
            ratio_w=float(2914)/float(self.ANNOTATION['width'])
            ratio_h=float(2404)/float(self.ANNOTATION['height'])
            for idx,rect in enumerate(self.ANNOTATION['boxlist']):
                xmin,ymin=rect['box'][0][0]*ratio_w,rect['box'][0][1]*ratio_h
                xmax,ymax=rect['box'][1][0]*ratio_w,rect['box'][1][1]*ratio_h
                contains0,contains1,contains2,contains3 = False,False,False,False                    
                if (corners[0]['x'] >= xmin  and corners[0]['x'] <= xmax and
                    corners[0]['y'] >= ymin  and corners[0]['y'] <= ymax ):
                    contains0=True
                if (corners[1]['x'] >= xmin  and corners[1]['x'] <= xmax and
                    corners[1]['y'] >= ymin  and corners[1]['y'] <= ymax ):
                    contains1=True
                if (corners[2]['x'] >= xmin  and corners[2]['x'] <= xmax and
                    corners[2]['y'] >= ymin  and corners[2]['y'] <= ymax ):
                    contains2=True
                if (corners[3]['x'] >= xmin  and corners[3]['x'] <= xmax and
                    corners[3]['y'] >= ymin  and corners[3]['y'] <= ymax ):
                    contains3=True
                if (contains0 and contains1 and contains2 and contains3):
                    return idx
                elif ( not contains0 and not contains1 and not contains2 and not contains3 ):
                    continue
                elif ( not contains0 and not contains1 and not contains2 and contains3 ):
                    continue
                elif ( not contains0 and not contains1 and contains2 and not contains3 ):
                    continue
                elif ( not contains0 and contains1 and not contains2 and not contains3 ):
                    continue
                elif ( contains0 and not contains1 and not contains2 and not contains3 ):
                    continue
                else:
                     xA,yA = max(xmin, corners[0]['x']),max(ymin, corners[0]['y'])
	                  #yA = max(ymin, corners[0]['y'])
                     xB,yB = min(xmax, corners[2]['x']),min(ymax, corners[2]['y'])
	                  #yB = min(ymax, corners[2]['y'])
                     interArea = (xB - xA + 1)*(yB - yA + 1)
                     boxBArea = (corners[2]['x'] - corners[0]['x'] + 1) * (corners[2]['y'] - corners[0]['y'] + 1)                                
                     if ( interArea/boxBArea < 0.6 ):
                          continue
                     else:
                          return idx
        except Exception as e:
            print(e)
            raise
        
if __name__ == '__main__':
    try:
        configFile = ConfigParser()
        configFile.read(ut.API_CONFIG_FILE)
        
        #Google cloude vision API Related Parameter
        ENDPOINT_URL = configFile.get('COMMONPARAMS','url')
        API_KEY= configFile.get('COMMONPARAMS','key')
        TYPE = configFile.get('COMMONPARAMS','type')
        
        #input image output DOC and Json Paths
        IMAGE_DIR = configFile.get('DB.Paths','DBIMAGEPATH')
        JSON_DIR = configFile.get('OCR.Paths','jsonpath')

        #TYpe of DOC and Other DEFAULT parameters
        MAKE_JSON = configFile.getboolean('OCR.DEFAULT','makejson')
        DOC_TYPE = configFile.get('OCR.DEFAULT','DB_DOC_TYPE')
        TEMPDIR = configFile.get('DB.Paths','TEMPDIR')
    except ConfigParser.ParsingError as e:
        sys.exit(e)
    except Exception as e:    
        sys.exit(e)     
    else:
        print('CONFIG FILE LOADED SUCESSFULLY ')
        makedirs(JSON_DIR, exist_ok=True)
        #makedirs(DB_DIR, exist_ok=True)
    finally:
        pass
    
    #Validating API_KEY and ENDPOINT_URL     
    if not API_KEY or not ENDPOINT_URL:
       sys.exit("API_KEY or ENDPOINT_URL is invalid")
    if (not exists(IMAGE_DIR))   :
        sys.exit("IMAGE_DIR is invalid")
    else:
        #IMAGE_FILENAMES=[ join(IMAGE_DIR,file) for file in listdir(IMAGE_DIR) 
        #                 if isfile(join(IMAGE_DIR, file))]
        IMAGE_FILENAME=['D://Python//Image//Transformed_Deotest50//Transformed_Deo_50_Benchmark_20180525_114343.jpg']
        #IMAGE_FILENAMES=['D://Python//database//Images//Deo//DEO51.jpg']         
    #Displaying Parameters 
    print("URL :{} , KEY :{}".format(ENDPOINT_URL,API_KEY))
    print(IMAGE_FILENAME) 
    #setting up Proxy
    proxy_url = "http://683898:Paramita@19@proxy.tcs.com:8080"
    environ['http_proxy'] = proxy_url 
    environ['HTTP_PROXY'] = proxy_url
    environ['https_proxy'] = proxy_url
    environ['HTTPS_PROXY'] = proxy_url
    # calling vision api
    
    try:
        filepath="D:/Python/Image/TF_output/TF_out_withtransformation/Transformed_Deo_50_Benchmark_withtransformation_55prod_TFout.csv"
        csvfile=If.csv2Box(filepath)
        tfDict_list=[]
        tfDict_list=csvfile.loadcsv();
        print("Total Number Of File Process "+ str(len(tfDict_list)))
        print("Processing File "+str(tfDict_list[0]['File']))
        shelfp=shelfProcessing(ENDPOINT_URL,API_KEY,TYPE,IMAGE_FILENAME,tfDict_list[0])
        #IMAGE_LIST=shelfp.CropBoxes(TEMPDIR)
        shelfp.ExtractText(IMAGE_FILENAME,JSON_DIR) 
        shelfp.DrawLeveledBoxes(TEMPDIR)
    except Exception as e:
        print(e)
        sys.exit(e)        
    else:
        print("NO EXCEPTION ")      
    finally:
        print("EXITING FROM CODE")