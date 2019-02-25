# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 16:38:42 2018

@author: 683898
"""

import csv 

class csv2Box:
    
    def __init__(self,csvFile):
        self.tfDict_list = []
        self.file=csvFile
        
    def row_count(self):
        with open(self.file) as in_file:
             return sum(1 for _ in in_file)
    
    def loadcsv(self):
        try:
            with open(self.file) as csvfile:
                 readCSV = csv.reader(csvfile, delimiter=',')
                 #readCSV.next()                 
                 next(readCSV)
                 previousRow=['defalt',0,0,0,0,0,0,0]
                 totalRowNum=self.row_count()-1
                 #tfDict_list=[]
                 #print("Total Number of Row :" +str(totalRowNum))
                 for line_num, row in enumerate(readCSV):
                     if line_num == 0:
                         boundingbox={'File':row[0],'width':row[1],'height':row[2],
                                      'OWIDTH':0,'OHEIGHT':0,'boxlist':[]}
                         leveldBox={'LEVEL':str('Deo'+row[3]),
                                    'TEXT':"",
                                    'OCRPREDICTION':"",
                                    'REMARK':"",
                                    'box':[(int(row[4]),int(row[5])),(int(row[6]),int(row[7]))]}
                         boundingbox['boxlist'].append(leveldBox)
                     elif line_num == totalRowNum-1:
                         #print("Total number Of box in "+previousRow[0]+" is :"+str(len(boundingbox['boxlist']))) 
                         self.tfDict_list.append(boundingbox.copy())
                         #boundingbox.clear()
                     else:
                         if (previousRow[0] != row[0]):
                             #print("Total number Of box in "+previousRow[0]+" is :"+str(len(boundingbox['boxlist']))) 
                             self.tfDict_list.append(boundingbox.copy())
                             #boundingbox.clear()                      
                             boundingbox['File']=row[0]
                             boundingbox['width']=row[1]
                             boundingbox['height']=row[2]
                             boundingbox['OWIDTH']=0
                             boundingbox['OHEIGHT']=0
                             boundingbox['boxlist']=[]
                             #{'File':row[0],'TEXT':None,'boxlist':[]}
                             leveldBox={'LEVEL':str('Deo'+row[3]),
                                        'TEXT':"",
                                        'OCRPREDICTION':"",
                                        'REMARK':"",
                                        'box':[(int(row[4]),int(row[5])),(int(row[6]),int(row[7]))]}
                             boundingbox['boxlist'].append(leveldBox)
                         else:
                             leveldBox={'LEVEL':str('Deo'+row[3]),
                                        'TEXT':"",
                                        'OCRPREDICTION':"",
                                        'REMARK':"",
                                        'box':[(int(row[4]),int(row[5])),(int(row[6]),int(row[7]))]}
                             boundingbox['boxlist'].append(leveldBox)
                     previousRow = row                
        except Exception as e:
             print(e)
             raise
        
if __name__ == '__main__':
    import sys
    import json
    try:
        filepath="D:/Python/Image/TF_output/TF_out_withouttransformation/WithoutTransformation_Deo_50_Benchmark_withouttransformation_55prod_TFout.csv"
        #filepath="D:/Python/Image/sample.csv"
        csvfile=csv2Box(filepath)
        tfDict_list=[]
        tfDict_list=csvfile.loadcsv();
        print("Total Number Of File Process "+ str(len(tfDict_list))) 
        #print(tfDict_list[0]['File'])
        r = json.dumps(tfDict_list[0])
        f = open("dict.json","w")
        f.write(str(r))
        f.close()
    except  Exception as e:
        print(e)
        sys.exit(e)
