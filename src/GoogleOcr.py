# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 13:40:10 2018

@author: 683898
"""
from os.path import join,basename
from base64 import b64encode 
import requests
import json

global TYPE,ENDPOINT_URL,API_KEY,JSON_DIR,IMAGE_DIR

class GCVOCR:
    def __init__(self,ENDPOINT_URL,API_KEY,TYPE,JSON_DIR,IMAGE_DIR):         
        self.ENDPOINT_URL = ENDPOINT_URL
        self.API_KEY=API_KEY
        self.TYPE=TYPE
        self.IMAGE_DIR=IMAGE_DIR
        self.JSON_DIR=JSON_DIR
     
    def ExtractOCR(self,FileName):
        try:
            img_requests = []
            FileName=join(self.IMAGE_DIR,FileName)
            with open(FileName, 'rb') as f:
                 ctxt = b64encode(f.read()).decode()
                 img_requests.append({'image': {'content': ctxt},
                               'features': [{'type': self.TYPE,'maxResults': 1}]})
            data=json.dumps({"requests": img_requests}).encode()
            response = requests.post(self.ENDPOINT_URL,data,
                           params={'key': self.API_KEY},                           
                           #proxies = {  "http"  : 'http://683898:Paramita@20@proxy.tcs.com:8080', 
                           #             "https" : 'http://683898:Paramita@20@proxy.tcs.com:8080'
                           #          },
                           headers={'Content-Type': 'application/json'}
                           )
            if ( response.status_code != 200 or response.json().get('error')):
                 errorMsg='Eorror Code : {} , Meg;{}'.format(response.status_code,
                                   'Eoor While GCV CALL') 
                 raise Exception(errorMsg)
            if False:     
                imgname = basename(FileName).split(".")[0]
                jpath = join(self.JSON_DIR,imgname + '.json')            
                for idx, resp in enumerate(response.json()['responses']):                   
                    with open(jpath, 'w') as f:
                         datatxt = json.dumps(resp, indent=2)
                         print("Wrote", len(datatxt), "bytes to", jpath)
                         f.write(datatxt)
        except requests.exceptions.HTTPError as e:
            print (e)
            raise
        except requests.exceptions.ConnectionError as e:
            print (e)   
            raise
        except requests.exceptions.ProxyError as e:
            print (e)   
            raise       
        except requests.exceptions.Timeout as e:
            print(e)
            raise             
        except KeyError as e:
            print(e)
            raise             
        except Exception as e:
            print(e)
            raise
        else:
            return response
    
    def ExtractText(self,ANNOTATION,HEIGHT,WIDTH):
        try:
            response=self.ExtractOCR(ANNOTATION['File'])
            if ( response.status_code != 200 or response.json().get('error')):
                 print("NOT RETURN ANY RESPONSE FROM GCV") 
                 raise KeyError
            #vt.VisionApi.write_ResponseJson(self,JSON_DIR,response,IMAGE_LIST)
            print(" GOOGLE OCR RUN ON IMAGE SUCESSFULLY")
            ratio_w=float(WIDTH)/float(ANNOTATION['width'])
            ratio_h=float(HEIGHT)/float(ANNOTATION['height'])
            TextSection=response.json()['responses'][0]['textAnnotations']
            for blocknum,block in enumerate(TextSection):
                if blocknum==0:
                    continue
                text=block['description']
                #print(text)
                corners=block['boundingPoly']['vertices']
                index = self.SearchBox(ANNOTATION,corners,ratio_w,ratio_h)
                if index is None:
                   #print ("INDEX NOT FOUND "+str(corners)) 
                   continue
                #print ("INDEX FOUND "+ str(index))                
                text=ANNOTATION['boxlist'][index]['TEXT']+text+" "
                ANNOTATION['boxlist'][index]['TEXT'] = text
            #Textonly=json.dumps(self.ANNOTATION,indent=2)
            #f = open("importent.json","w")
            #f.write(Textonly)
            #f.close()            
        except KeyError as e:
            print(e)
            raise    
        except Exception as e:
            print(e)
            raise
        
    def SearchBox(self,ANNOTATION,corners,ratio_w,ratio_h):        
        try:
            for idx,rect in enumerate(ANNOTATION['boxlist']):
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
                     if  boxBArea == 0:
                         return None                               
                     if ( abs(interArea/boxBArea) < 0.6 ):
                          continue
                     else:
                          return idx
        except KeyError as e:
            print(e)
            return None              
        except Exception as e:
            print('Module :{} ,Error :{}'.format(__name__,e))
            raise

if __name__ == '__main__':
   from configparser import ConfigParser
   import utility as ut
   configFile = ConfigParser()
   configFile.read(ut.API_CONFIG_FILE)
   ENDPOINT_URL = configFile.get('OCRPARAM','url')
   API_KEY= configFile.get('OCRPARAM','key')
   TYPE = configFile.get('OCRPARAM','type')
   IMAGE_DIR = configFile.get('Paths','imagepath')
   IMAGE_FILENAME="20180627_095634.jpg"
   JSON_DIR = configFile.get('Paths','jsonpath')
   ocr=GCVOCR(ENDPOINT_URL,API_KEY,TYPE,JSON_DIR,IMAGE_DIR)
   ocr.ExtractOCR(IMAGE_FILENAME)
