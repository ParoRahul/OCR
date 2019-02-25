# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 17:29:13 2018

@author: 683898
"""
import sys

try:
    import cElementTree as ET
except ImportError:
  try:
    # Python 2.5 need to import a different module
    import xml.etree.cElementTree as ET
  except ImportError:
    sys.exit("Failed to import cElementTree from any known place") 

class configFile:
    """Construct and use the ConfigFile calss for Hyper paraemeter Uploading."""
    def __init__(self,api_config_file='config.xml' ):
        try:
            self.config = ET.parse(open(api_config_file, "r"))
            self.root = self.config.getroot()
            self.child = [child.tag for child in self.root]
            #for child in self.root:
            #    child.append(child.tag)
            #print(self.root.tag)
            self.nameValuePair = {}
            for k in  self.child:   
                element = self.root.find(k)
                for e in element.iter('level'):
                    name=element.tag+'.'+str(e.get('name'))
                    self.nameValuePair[name]=e.get('value')
                    #print (e.attrib['name'],e.get('name'),element.tag)

        except:
            sys.exit("Unable to open or parse input definition file: " + api_config_file)
            
    def getParams(self,tagDotTag):
        try:
            [tag,subtag] = tagDotTag.split(".")
            if tag not in self.child:
               return None
            return self.nameValuePair.get(tagDotTag)             
        except:
            sys.exit("Unable to open and parse input definition file: " + tagDotTag)