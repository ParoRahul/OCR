# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 23:08:33 2018

@author: 683898
"""

import requests
import json

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
           URL='http://{}:{}/solr/{}/select?q=*:*&spellcheck.q={}&spellcheck=on'.format(self.HOSTID,self.PORT,self.SPELLCHECK_CORE,main_query)
           print(URL)
           proxies = { 'http': 'http://683898:Paramita@19@proxy.tcs.com:8080', 
                       'https': 'http://683898:Paramita@19@proxy.tcs.com:8080'}
           headers = {'content-type': "application/json" }
           response  = requests.post(URL,proxies=proxies,data=json.dumps({}), headers=headers)
           print("---")
           print(response)
           suggestions=response.json()["spellcheck"]["suggestions"]
           print(type(suggestions), len(suggestions))
           correctdWordList=[]
           for string,dictonary in zip(suggestions[0::2], suggestions[1::2]):
               correctedDict={string:dictonary['suggestion']}
               correctdWordList.append(correctedDict)
           print(correctdWordList)    
        except Exception as e:
            print(e)
            raise


if __name__ == '__main__':
   import os
   print(os.environ.get('HTTPS_PROXY'))
   print(os.environ.get('HTTP_PROXY'))
   HOSTID="10.171.33.241"
   PORT="8983"
   CORE1="DEO"
   CORE2="DEO_PRODUCT"
   listofWords=['bodi','spry']
   solr=solr(HOSTID,PORT,CORE1,CORE2)
   solr.request_spellCheck(listofWords)            