# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 00:56:53 2018

@author: 683898
"""
import math
from os import listdir,rename
from os.path import exists,isfile,join,basename
import json

API_CONFIG_FILE='D:/Python/TF_interface/config/config.ini'


def extract_OppositeVertices(corners):
    """ Extract two opposite vertices from list of 4 corners of any rect"""
    min_x,max_x,min_y,max_y=math.inf,-math.inf,math.inf,-math.inf
    for point in corners:            
        if point.get('x',min_x)<min_x:
            min_x=point.get('x') if point.get('x') > 0.0 else 0.0 
        if point.get('x',max_x)>max_x:
            max_x=point.get('x')
        if point.get('y',min_y)<min_y:
            min_y=point.get('y') if point.get('y') > 0.0 else 0.0
        if point.get('y',max_y)>max_y:
            max_y=point.get('y')
    #print (min_x,max_x,min_y,max_y)
    return (int(min_x),int(min_y)),(int(max_x),int(max_y))

def Merge_txtFiles(PATH):
    try:
        if (not exists(PATH)):
            print("invalid Path "+ PATH)
            return
        filelist = [ join(PATH, f)  for f in listdir(PATH)  if isfile(join(PATH, f))]        
        print('Total number File to be merged #'+str(len(filelist)))
#       with open(join(PATH,'MERGED_FILE.txt'), 'w') as outfile:
#            for file in filelist:
#                with open(file) as infile:
#                     tag=basename(file).split(".")[0]
#                     data=tag+"#"+infile.read()+"\n"
#                     outfile.write(data)
        data=[]
        with open(join(PATH,'MERGED_FILE.json'), 'w') as outfile:
            for file in filelist:
                with open(file) as infile:
                     tag=basename(file).split(".")[0]
                     text=infile.read()
                     data.append({'Level':tag,'Text':text})
            json.dump(data,outfile,indent=2)
        print(" Out file generated "+ 'MERGED_FILE.txt')            
    except IOError as e:
        print(e)
    except Exception as e:
        print(e)
        
def Rename_fileList(PATH):        
    try:
        if (not exists(PATH)):
            print("invalid Path "+ PATH)
            return
        imagetype=['jpg','JPEG','JPG','png','PNG']
        filelist = [  f  for f in listdir(PATH)  
                     if isfile(join(PATH, f)) and f.split('.')[1] in imagetype ] 
        for file in filelist:
            newfile=file[39:]
            print("changing {} to {}".format(file,newfile))
            rename(join(PATH,file),join(PATH,newfile))    
    except IOError as e:
        print(e)
    except Exception as e:
        print(e)    