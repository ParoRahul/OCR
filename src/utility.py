# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 00:56:53 2018

@author: 683898
"""
import math
from os import listdir,rename
from os.path import exists,isfile,join,basename
import json

API_CONFIG_FILE='D:/OCR/config/config.ini'


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
        print(" Out file generated "+ 'MERGED_FILE.json')            
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
        
        
def DrawOCRDATA(IMAGEPath, BOXDETAILS):
    try:
        import cv2
        img = cv2.imread(IMAGEPath)
        height, width, channels = img.shape
        ratio_w=float(width)/float(BOXDETAILS['width'])
        ratio_h=float(height)/float(BOXDETAILS['height'])
        fileName=BOXDETAILS['File']
        for box in BOXDETAILS['boxlist']:
            #text=box['TEXT']
            levl1=box['LEVEL']
            levl2=box['OCRPREDICTION']
            corners=box['box']
            c1=(int(corners[0][0]*ratio_w),int(corners[0][1]*ratio_h))
            c2=(int(corners[1][0]*ratio_w),int(corners[1][1]*ratio_h))
            c3=(int(0.5*(corners[0][0]*ratio_w+corners[1][0]*ratio_w)),
                    int((corners[0][1]*ratio_h+corners[1][1]*ratio_h)*0.5))
            cv2.rectangle(img,c1,c2,(0,255,0),5)
            #cv2.putText(img,text,c1,cv2.FONT_HERSHEY_SIMPLEX,2,(255,2,255),2)
            cv2.putText(img,levl1,c1,cv2.FONT_HERSHEY_SIMPLEX,2,(255,0,255),2)
            cv2.putText(img,levl2,c3,cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,0),2)
        ocrimageName = join('D:/OCR/Output/Image',fileName.split(".")[0] +'_OCR.'+ fileName.split(".")[1])
        cv2.imwrite(ocrimageName,img)
    except Exception as e:
        print(e)
        
def Json2Csv(InDIR):       
    try:
        from os.path import exists,join
        from os import listdir
        import json,csv
        if (not exists(InDIR)):
            raise Exception("Input Path not valid")
        FileList=[join(InDIR,file) for file in listdir(InDIR) if file.split('.')[1]=='json' ]    
        with open('Deo.csv', 'w') as outfile:
            fieldnames = ['filename','width','height','classes','xmin','ymin','xmax','ymax']
            writer = csv.DictWriter(outfile ,fieldnames=fieldnames)
            writer.writeheader()
            for file in FileList:
                with open(file, 'r') as f:
                    datastore = json.load(f)
                    ratio_w=float(datastore['OWIDTH'])/float(datastore['width'])
                    ratio_h=float(datastore['OHEIGHT'])/float(datastore['height'])            
                    for box in datastore['boxlist']:
                        rowDict={
                                'filename':datastore['File'],
                                'width':datastore['width'],
                                'height':datastore['height'],
                                'classes':box['OCRPREDICTION'],
                                'xmin':int(box['box'][0][0]*ratio_w),
                                'ymin':int(box['box'][0][1]*ratio_h),
                                'xmax':int(box['box'][1][0]*ratio_w),
                                'ymax':int(box['box'][1][1]*ratio_h)    
                                }
                        writer.writerow(rowDict)
    except Exception as e:
            print(e)
            
if __name__ == '__main__':   
   Json2Csv('D:/OCR/Output/Json')         