# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 23:08:33 2018

@author: 683898
"""

import requests
#import json

class solr:
    def __init__(self,HOSTID,PORT,SPELLCHECK_CORE,QUERY_CORE):
        self.HOSTID=HOSTID
        self.PORT=PORT
        self.SPELLCHECK_CORE=SPELLCHECK_CORE
        self.QUERY_CORE=QUERY_CORE
        
    
    def request_spellCheck(self,listofWords):
        try:
           main_query=""
           numberOfWord=len(listofWords)
           for id,word in enumerate(listofWords):
               if numberOfWord==1:
                  main_query=word
               else:   
                  if id ==0 :
                     main_query=word+'%20AND%20'
                  elif id == numberOfWord-1:
                     main_query=main_query+word
                  else:   
                     main_query=main_query+word+'%20AND%20'
           MAINURL='http://localhost:{}/solr/{}/'.format(self.PORT,self.SPELLCHECK_CORE)          
           URL='{}select?q=*:*&spellcheck.q={}&spellcheck=on'.format(MAINURL,main_query)
           #print(URL)
           session = requests.Session()
           response=session.get(URL)
           if ( response.status_code != 200 or response.json().get('error')):
                errorMsg='Eorror Code : {} , Meg;{}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
                raise Exception(errorMsg)
           if response.json()['responseHeader']['status'] !=0:     
              errorMsg='Eorror Code : {} , Meg;{}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
              raise Exception(errorMsg)
           suggestions=response.json()["spellcheck"]["suggestions"]
           correctdWordList=[]
           if not suggestions:
              for word in listofWords:
                  correctdWordList.append({word:[word]})
           else:       
               for string,dictonary in zip(suggestions[0::2], suggestions[1::2]):
                   correctedDict={string:dictonary['suggestion']}
                   correctdWordList.append(correctedDict)
           #print(correctdWordList)
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
        except Exception as e:
            print(e)
            raise
        else:
            return correctdWordList
            
    def Prepare_queryStatement(self,txtFromGCV):
        try:
            listofWords=txtFromGCV.split()
            correctdWordList=self.request_spellCheck(listofWords)
            Correctedtext=""
            numberofWord=len(listofWords)
            for id,word in enumerate(listofWords):
                dictOrfalse=next((w for w in correctdWordList if word in w.keys()),False)
                if numberofWord==1:
                    if dictOrfalse:
                       Correctedtext='Text:'+dictOrfalse[word][0]
                    else:   
                       Correctedtext='Text:'+word
                else:
                    if id < numberofWord-1:
                        if dictOrfalse:
                           Correctedtext=Correctedtext+'Text:'+dictOrfalse[word][0]+'%20AND%20'
                        else:   
                           Correctedtext=Correctedtext+'Text:'+word+'%20AND%20'
                    else:
                        if dictOrfalse:
                           Correctedtext=Correctedtext+'Text:'+dictOrfalse[word][0]
                        else:   
                           Correctedtext=Correctedtext+'Text:'+word
           # print(Correctedtext)            
        except Exception as e:
            print(e)
            raise
        else:
            return Correctedtext
            
    def request_ProductId(self,Strings):
        try:
           MAINURL='http://localhost:{}/solr/{}/'.format(self.PORT,self.QUERY_CORE)          
           URL='{}select?q={}'.format(MAINURL,Strings)
           #print(URL)
           session = requests.Session()
           response=session.get(URL)
           if ( response.status_code != 200 or response.json().get('error')):
                errorMsg='Eorror Code : {} , Meg;{}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
                raise Exception(errorMsg)
           if response.json()['responseHeader']['status'] !=0:
              errorMsg='Eorror Code : {} , Meg;{}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
              raise Exception(errorMsg)
           numberOfDocFound=response.json()["response"]["numFound"]     
           print('Total number of Document Found : {}'.format(numberOfDocFound))
           LevelList=[]
           for docs in response.json()["response"]["docs"]:
               LevelList.extend(docs['Level'])
           print(LevelList)
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
        except Exception as e:
            print(e)
            raise   
        except Exception as e:
            print(e)
            raise        


if __name__ == '__main__':
   import os
   print(os.environ.get('HTTPS_PROXY'))
   print(os.environ.get('HTTP_PROXY'))
   HOSTID="10.171.33.241"
   PORT=8983
   CORE1="DEO"
   CORE2="DEOProduct"
   listofWords='WIND SONG Extraordinary Fragrance Gentle Deodorant Body Spray'
   solr=solr(HOSTID,PORT,CORE1,CORE2)
   Correctedtext=solr.Prepare_queryStatement(listofWords)
   solr.request_ProductId(Correctedtext)