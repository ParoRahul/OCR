from os.path import exists,isfile,join,basename
from base64 import b64encode 
import json
import requests
import cv2


class VisionApi:
   
    def __init__(self,ENDPOINT_URL,API_KEY,TYPE):
        
        """Construct a wrapper of Google Vision API service.
    
        Args:
            ENDPOINT_URL -- Google Cloude Vision URL
                            https://vision.googleapis.com/v1/images:annotate 
            API_KEY      -- Google Cloude Vision API Key
            TYPE         -- TEXT_DETECTION/DOCUMENT_TEXT_DETECTION
          
        Methods:    
            make_image_data_list -- Does image data predation for GCV OCR
            request_ocr          -- Call the GCV OCR with image file prepared by
                                    make_image_data_list
            process_response     -- Process the response data write JSON to Path 
        """        
        self.ENDPOINT_URL = ENDPOINT_URL
        self.API_KEY=API_KEY
        self.TYPE=TYPE
        
    def make_image_data_list(self,IMAGE_FILENAMES):
        """ Does image data predation for GCV OCR """
        try:
            img_requests = []
            for imgname in IMAGE_FILENAMES:
                with open(imgname, 'rb') as f:
                    ctxt = b64encode(f.read()).decode()
                    img_requests.append({'image': {'content': ctxt},
                                         'features': [{'type': self.TYPE,
                                         'maxResults': 1}]
                    })
        except Exception as e:
            print(e)
            raise
        else:
            return json.dumps({"requests": img_requests}).encode()
    
    def request_ocr(self,IMAGE_FILENAMES):
        """ Call the GCV OCR with image file prepared by make_image_data_list """
        try:
            data=self.make_image_data_list(IMAGE_FILENAMES)
            if not data:
               raise Exception
            response = requests.post(self.ENDPOINT_URL,data,
                       params={'key': self.API_KEY},
                       headers={'Content-Type': 'application/json'})
        except KeyError as e:
            print(e)
            raise
        except Exception as e:
            print(e)
            raise
        else:
            return response
        
    def process_response(self,MAKE_JSON,JSON_DIR,RESPONSE,IMAGE_FILENAMES):
        """ Process the response data write Documents of JSON to Path """
        try:
            text_response = {}
            for idx, resp in enumerate(RESPONSE.json()['responses']):                   
                imgname = basename(IMAGE_FILENAMES[idx])
                if 'textAnnotations' in resp:
                     text_response[imgname] = resp['textAnnotations']
                else:
                     text_response[imgname] = []    
        except Exception as e:
            print(e)
            raise
        else:
            return text_response

    def write_ResponseJson(self,JSON_DIR,RESPONSE,IMAGE_FILENAMES):
        """ Process the response data write COMPLETE JSON to Path """
        try:
            for idx, resp in enumerate(RESPONSE.json()['responses']):                   
                imgname = basename(IMAGE_FILENAMES[idx]).split(".")[0]
                jpath = join(JSON_DIR, imgname + '.json')
                with open(jpath, 'w') as f:
                     datatxt = json.dumps(resp, indent=2)
                     print("Wrote", len(datatxt), "bytes to", jpath)
                     f.write(datatxt)
        except Exception as e:
            print(e)
            raise
        else:
            return
        
    def write_textonly(self,DB_DIR,RESPONSE,IMAGE_FILENAMES,DOC_TYPE):
        """ Process the response data write text to Path """
        try:
            for idx, resp in enumerate(RESPONSE.json()['responses']):                   
                imgname = basename(IMAGE_FILENAMES[idx]).split(".")[0]
                if DOC_TYPE=='txt':
                    jpath = join(DB_DIR, imgname + '.txt')
                    datatxt = resp['fullTextAnnotation']['text'].replace('\n', ' ')
                    datatxt = datatxt.encode('ascii','ignore').decode("utf-8")
                    #print(datatxt.encode("utf-8"))
                    with open(jpath, 'w') as f:
                         #datatxt = json.dumps(resp, indent=2)
                         print("Wrote", len(datatxt), "bytes to", jpath)
                         f.write(datatxt)
                elif DOC_TYPE=='json':
                    jpath = join(DB_DIR, imgname + '.json')
                    with open(jpath, 'w') as f:
                         datatxt = json.dumps(resp['fullTextAnnotation']['text'], indent=2)
                         print("Wrote", len(datatxt), "bytes to", jpath)
                         f.write(datatxt)                    
        except Exception as e:
            print(e)
            raise
        else:
            return    
            
    def capture_output(self,text_response,IMAGE_DIR,JSON_DIR):
        """ Reprint image with OCR Text and Bounding Box """
        try:
            for fileName in text_response:                   
                imgname = join(IMAGE_DIR, basename(fileName))
                #print(fileName)
                im = cv2.imread( imgname )
                for field in text_response[fileName]:
                    text=field['description']
                    corners=field['boundingPoly']['vertices']
                    c1,c2=ut.extract_OppositeVertices(corners)
                    #canvas.rectangle(OppositeVertices,fill="black")
                    #canvas.text(OppositeVertices[0],text,(0,0,0))
                    #print(field)
                    cv2.rectangle(im,c1,c2,(0,0,255),5)
                    cv2.putText(im,text,c1,cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,0,0))
                ocrimageName = join(JSON_DIR,fileName.split(".")[0] +
                             '_OCR.'+ fileName.split(".")[1])
                #print(ocrimageName)
                cv2.imwrite(ocrimageName,im)
        except KeyError as e:
               print(e)
               raise
        except IOError  as e:
               print(e)
               raise       
        except Exception as e:
            print(e)
            raise
        else:
            return 
#nend of VisionApi Class defination   


if __name__ == '__main__':
    from os import listdir, makedirs
    import sys
    from configparser import ConfigParser
    import utility as ut
    try:
        configFile = ConfigParser()
        configFile.read(ut.API_CONFIG_FILE)        
        #Google cloude vision API Related Parameter
        ENDPOINT_URL = configFile.get('COMMONPARAMS','url')
        API_KEY= configFile.get('COMMONPARAMS','key')
        TYPE = configFile.get('COMMONPARAMS','type')
        
        #input image output DOC and Json Paths
        IMAGE_DIR = configFile.get('OCR.Paths','inputimagepath')
        DB_DIR = configFile.get('OCR.Paths','dbdocpath')
        JSON_DIR = configFile.get('OCR.Paths','jsonpath')

        #TYpe of DOC and Other DEFAULT parameters
        MAKE_JSON = configFile.getboolean('OCR.DEFAULT','makejson')
        DOC_TYPE = configFile.get('OCR.DEFAULT','DB_DOC_TYPE')
        
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
    if (not exists(IMAGE_DIR))   :
        sys.exit("IMAGE_DIR is invalid")
    else:
        IMAGE_FILENAMES=[ join(IMAGE_DIR,file) for file in listdir(IMAGE_DIR) 
                          if isfile(join(IMAGE_DIR, file))]
    #Displaying Parameters 
    print("URL :{} , KEY :{}".format(ENDPOINT_URL,API_KEY))
    print(IMAGE_FILENAMES)
    #IMAGE_FILENAME=['D:\\Python\\Image\\TF_output\\TF_out_withouttransformation\\WithoutTransformation_Deo_50_Benchmark_20180525_114026.jpg']         
    # calling vision api
    try:
        visionApi = VisionApi(ENDPOINT_URL,API_KEY,TYPE)
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
           print(type(text_response), type(response))
           print(text_response.keys())
           visionApi.write_ResponseJson(JSON_DIR,response,IMAGE_FILENAMES)
           #visionApi.write_textonly(DB_DIR,response,IMAGE_FILENAMES,DOC_TYPE)
           visionApi.capture_output(text_response,IMAGE_DIR,JSON_DIR)
    finally:
         print("EXITING FROM CODE")