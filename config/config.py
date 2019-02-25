# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 01:50:44 2018

@author: 683898
"""

import sys
from configparser import ConfigParser

class configFile:
    """Construct and use the ConfigFile calss for Hyper paraemeter Uploading."""
    def __init__(self,api_config_file='config.int' ):
        try:
            self.config = ConfigParser() 
            self.config.read(api_config_file)
        except Exception as e:
            print(e)
            sys.exit("Unable to open or parse input definition file: " + api_config_file)
            
    def getParams(self,tagDotTag):
        try:
            [tag,subtag] = tagDotTag.split(".")
            if tag not in self.config:
               return None
            return self.config.get(tag,subtag)             
        except Exception as e:
            print(e)