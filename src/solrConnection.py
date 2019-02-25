# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 23:08:33 2018

@author: 683898
"""

import requests
#import json

class solr:
    def __init__(self,HOSTID,PORT,QUERY_CORE,REMOTE_HOST=False):
        self.HOSTID=HOSTID
        self.PORT=PORT
        self.QUERY_CORE=QUERY_CORE
        if REMOTE_HOST:
           self.URL='http://{}:{}/solr/{}'.format(self.HOSTID,self.PORT,self.QUERY_CORE)
        else:              
           self.URL='http://localhost:{}/solr/{}'.format(self.PORT,self.QUERY_CORE)
        print('URL {}'.format(self.URL))
        
    def stringModifier(self,textString,operator):
        listofWords=textString.split()
        modified_string=""
        modifiedList=[ word for word in listofWords if len(word) >= 2 ]  
        if not modifiedList:
           return 0,None 
        numberOfWord=len(modifiedList)
        if operator=='AND':
           opp=' AND '
        elif operator=='TAND':
            opp='~ AND '
        elif operator=='OR':    
            opp=' OR '
        elif operator=='TOR':    
            opp='~ OR '
        else:
            opp=' '
        for id,word in enumerate(modifiedList):            
            if numberOfWord==1:
               if operator in ['TAND', 'TOR']:
                   modified_string='Text:\''+word+'\'~'
               elif operator in ['spell']:  
                   modified_string='\''+word+'\''
               else:
                   modified_string='Text:\''+word+'\''
            else:   
               if id ==0 :
                  if operator in ['spell']:
                     modified_string='\''+word+'\' AND '
                  else:   
                     modified_string='Text:\''+word+'\''+opp
               elif id == numberOfWord-1:
                  if operator in ['TAND','TOR']: 
                     modified_string=modified_string+'Text:\''+word+'\'~'
                  elif operator in ['spell']:
                     modified_string=modified_string+'\''+word+'\'' 
                  else:   
                     modified_string=modified_string+'Text:\''+word+'\''
               else:
                  if  operator in ['spell']:
                      modified_string=modified_string+'\''+word+'\''
                  else:    
                      modified_string=modified_string+'Text:\''+word+'\''+opp
        return   numberOfWord,modified_string
     
    def request_spellCheck(self,textstring):
        try:
           length,main_query=self.stringModifier(textstring,'spell')
           print(main_query)
           SPELL_CHECK_URL='{}/spell?'.format(self.URL)
           params={
                    "spellcheck.q" :main_query,
                    "spellcheck":"on",
	                 "wt":"json",
                    "rows":"10"
                  }
           print(SPELL_CHECK_URL)
           session = requests.Session()
           response=session.get(SPELL_CHECK_URL,params=params)
           print(response.status_code)
           if ( response.status_code != 200 or response.json().get('error')):
                errorMsg='Eorror Code : {} , Meg : {}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
                raise Exception(errorMsg)
           if response.json()['responseHeader']['status'] !=0:     
              errorMsg='Eorror Code : {} , Meg : {}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
              raise Exception(errorMsg)
           suggestions=response.json()["spellcheck"]["suggestions"]
           correctdWordList=[]
           if not suggestions:
              for word in textstring.split():
                  correctdWordList.append({word:[word]})
           else:       
               for string,dictonary in zip(suggestions[0::2], suggestions[1::2]):
                   correctedDict={string:dictonary['suggestion'][0]['word']}
                   correctdWordList.append(correctedDict)
           retText=""        
           for word in textstring.split():
               wordFound=next((item for item in correctdWordList if word in item.keys() ), False)
               if wordFound:
                  retText=retText+' '+ wordFound[word]
               else:
                  retText=retText+' '+ word  
           print(correctdWordList,retText)
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
            return retText
            
    def request_ProductId(self,txtString):
        try:
           length,Main_qry=self.stringModifier(txtString,'TAND') 
           QUERY_URL='{}{}/select?'.format(self.URL,self.QUERY_CORE)
           params={
                   "q" :"Text:"+Main_qry,
                   "fl":"Level,Text,score",
	                "wt":"json" ,
                   "rows":"10"
                  }
           print(QUERY_URL,Main_qry)
           session = requests.Session()
           response=session.get(QUERY_URL,params=params)
           print(response.status_code)
           if ( response.status_code != 200 or response.json().get('error')):
                errorMsg='Eorror Code : {} , Meg: {}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
                raise Exception(errorMsg)
           if response.json()['responseHeader']['status'] !=0:
              errorMsg='Eorror Code : {} , Meg: {}'.format(response.json()['error']['code'],
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
        else:
           return LevelList
       
    def request_ORQuery(self,txtString):
        try:
           length,Main_qry=self.stringModifier(txtString,'OR')
           if Main_qry is None :
              return None
           print(Main_qry)
           QUERY_URL='{}/select?'.format(self.URL)
           params={
                   "q" :Main_qry,
                   "fl":"Level,Text,score",
	                "wt":"json",
                   "rows":"10"
                  }
           print(QUERY_URL)
           session = requests.Session()
           response=session.get(QUERY_URL,params=params)
           print(response.status_code)
           levelList=[]
           if ( response.status_code != 200 or response.json().get('error')):
                errorMsg='Eorror Code : {} , Meg: {}'.format(response.json()['error']['code'],
                                   response.json()['error']['msg']) 
                raise Exception(errorMsg)
           if response.json()['responseHeader']['status'] !=0:
              errorMsg='Eorror Code : {} , Meg: {}'.format(response.json()['error']['code'],
                        response.json()['error']['msg']) 
              raise Exception(errorMsg)
           numberOfDocFound=response.json()["response"]["numFound"]     
           print('Total number of Document Found : {}'.format(numberOfDocFound))
           #print(response.json()["response"])
           if numberOfDocFound==0:
              return None
           maxScore=response.json()["response"]['maxScore']
           levelList=[doc["Level"][0] for doc in response.json()["response"]["docs"] 
                       if doc["score"]==maxScore]
           print('levelList :',levelList)
        except requests.exceptions.HTTPError as e:
           print (e)
           return None
        except requests.exceptions.ConnectionError as e:
           print (e)
           return None
        except requests.exceptions.ProxyError as e:
           print (e)   
           return None   
        except requests.exceptions.Timeout as e:
           print(e)
           return None
        except Exception as e:
           print(e)
           return None   
        except Exception as e:
           print(e)
           return None  
        else:
           return levelList
    


if __name__ == '__main__':
   import os
   import sys
   from configparser import ConfigParser
   import utility as ut
   configFile = ConfigParser()
   configFile.read(ut.API_CONFIG_FILE)
   print('CONFIG FILE LOADED SUCESSFULLY')
   print(os.environ.get('HTTPS_PROXY'))
   print(os.environ.get('HTTP_PROXY'))
   HOSTID=configFile.get('SOLRPARAM','hostid')
   PORT=configFile.get('SOLRPARAM','port')
   CORE=configFile.get('SOLRPARAM','query_core')
   if HOSTID and PORT and CORE:
       print('Host id : {}, Port : {}, Core :{}'.format(HOSTID,PORT,CORE))
   else:
       sys.exit("INAVALID PARAMETER ")
   listofWords='WOMA boylicious'
   solr=solr(HOSTID,PORT,CORE)
   #Correctedtext=solr.request_ORQuery(listofWords)
   solr.request_spellCheck(listofWords)
   #solr.request_ProductId(Correctedtext)