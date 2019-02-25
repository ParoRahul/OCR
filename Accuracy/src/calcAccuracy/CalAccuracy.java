package calcAccuracy;

import java.io.BufferedWriter;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;

public class CalAccuracy {
	public static String dataset = "Deo";//"LC";//"Deo";
	public static String path = "D:/OCR/Inputs/Tfcsv/";
	public static HashMap<String,ArrayList<HashMap<String,String>>> outputMap = new HashMap<String,ArrayList<HashMap<String,String>>>();
	public static HashMap<String,ArrayList<HashMap<String,String>>> gtMap = new HashMap<String,ArrayList<HashMap<String,String>>>();
	public static ArrayList<String> fileArray = new ArrayList<String>();
	public static BufferedWriter bw;
	
	public static double overlapThresh = 0.5;//0.01;	
		
	public static void main(String[] args) {
		readFile("O");//Output
		readFile("G");//Ground Truth
		Collections.sort(fileArray);
		
		try {
			bw = new BufferedWriter(new FileWriter(path+dataset+" Accuracy Table.csv"));
			bw.write(",,,GT Based,,,,ROI Based,,,,Full Image Based,,,\n");
			bw.write("FileName,TP,FN,FP,Recall,Precision,Accuracy(F1),FP,Recall,Precision,Accuracy(F1),FP,Recall,Precision,Accuracy(F1)\n");
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		for(String fileName:fileArray) {
			processEach(fileName);
		}	
		
		try {
			bw.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}	

	private static void processEach(String fileName) {
		ArrayList<HashMap<String,String>> rackInfoList = outputMap.get(fileName);
		ArrayList<HashMap<String,String>> gtInfoList = gtMap.get(fileName);
		
		int tp = getTruePositiveCount(gtInfoList,rackInfoList);
		int fpG = getFalsePositiveCount(gtInfoList,rackInfoList,"G");//G=Ground Truth;R=ROI;A=All
		int gtObjeCount = gtInfoList.size();
		int fn = gtObjeCount - tp;
		
		double recall = (double) tp/gtObjeCount;
		double precisionG = (double) tp / (tp + fpG);
		double accuracyG = 0;
		try {
			accuracyG = (2 / ((1 / precisionG) + (1 / recall))) * 100;
		} catch(Exception ex) {
			accuracyG = 0;
		}
		
		int fpR = getFalsePositiveCount(gtInfoList,rackInfoList,"R");//G=Ground Truth;R=ROI;A=All
		double precisionR = (double) tp / (tp + fpR);
		double accuracyR = 0;
		try {
			accuracyR = (2 / ((1 / precisionR) + (1 / recall))) * 100;
		} catch(Exception ex) {
			accuracyR = 0;
		}
		
		int fpA = getFalsePositiveCount(gtInfoList,rackInfoList,"A");//G=Ground Truth;R=ROI;A=All
		double precisionA = (double) tp / (tp + fpA);
		double accuracyA = 0;
		try {
			accuracyA = (2 / ((1 / precisionA) + (1 / recall))) * 100;
		} catch(Exception ex) {
			accuracyA = 0;
		}
		
//		System.out.println(fileName + ":" + recall*100);
		try {
			bw.write(fileName + "," + tp + "," + fn + "," + fpG + "," + recall + "," + precisionG + "," + accuracyG + "," + fpR + "," + recall + "," + precisionR + "," + accuracyR + "," + fpA + "," + recall + "," + precisionA + "," + accuracyA + "\n");
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}	

	private static int getTruePositiveCount(ArrayList<HashMap<String, String>> gtInfoList,
			ArrayList<HashMap<String, String>> rackInfoList) {
		
		int objDetected = 0;
		
		for(HashMap<String, String> gtObj:gtInfoList) {
			objDetected+=checkDetected(gtObj,rackInfoList);
		}
		
		return objDetected;
	}
	
	private static int getFalsePositiveCount(ArrayList<HashMap<String, String>> gtInfoList,
			ArrayList<HashMap<String, String>> rackInfoList, String basisOfFPSearch) {
		int fpCount = 0;
		if("G".equals(basisOfFPSearch)) {
			for(HashMap<String, String> gtObj:gtInfoList) {
				fpCount+=checkFalseDetected(gtObj,rackInfoList);
			}
		}
		else if("R".equals(basisOfFPSearch)) {
			fpCount = getFPCountWithinROI(gtInfoList,rackInfoList);
		}
		else {
			for(HashMap<String, String> tempRCK:rackInfoList) {
				if(!tempRCK.containsKey("matched")) {
					fpCount++;
				}
			}
		}
		
		
		return fpCount;
	}	

	private static int getFPCountWithinROI(ArrayList<HashMap<String, String>> gtInfoList,
			ArrayList<HashMap<String, String>> rackInfoList) {
		double xminROI = Double.MAX_VALUE;
		double yminROI = Double.MAX_VALUE;
		double xmaxROI = Double.MIN_VALUE;
		double ymaxROI = Double.MIN_VALUE;
		
		double gtWidth = Double.parseDouble(gtInfoList.get(0).get("width")); 
		double gtHeight = Double.parseDouble(gtInfoList.get(0).get("height"));
		
		double rckWidth = Double.parseDouble(rackInfoList.get(0).get("width"));
		double rckHeight = Double.parseDouble(rackInfoList.get(0).get("height"));
		
		double xResizeFactor = gtWidth/rckWidth;
		double yResizeFactor = gtHeight/rckHeight;
		
		for(HashMap<String, String> tempGT:gtInfoList) {
			double gtxmin = Double.parseDouble(tempGT.get("xmin"));
			double gtymin = Double.parseDouble(tempGT.get("ymin"));
			double gtxmax = Double.parseDouble(tempGT.get("xmax"));
			double gtymax = Double.parseDouble(tempGT.get("ymax"));
			
			if(gtxmin < xminROI) {	xminROI = gtxmin; }
			if(gtymin < yminROI) {	yminROI = gtymin; }
			if(gtxmax > xmaxROI) {	xmaxROI = gtxmax; }
			if(gtymax > ymaxROI) {	ymaxROI = gtymax; }
		}
		
		int fpCount = 0;
		
		for(HashMap<String, String> tempRCK:rackInfoList) {
			if(!tempRCK.containsKey("matched")) {
				double rckxmin = Double.parseDouble(tempRCK.get("xmin"))*xResizeFactor;
				double rckymin = Double.parseDouble(tempRCK.get("ymin"))*yResizeFactor;
				double rckxmax = Double.parseDouble(tempRCK.get("xmax"))*xResizeFactor;
				double rckymax = Double.parseDouble(tempRCK.get("ymax"))*yResizeFactor;
				
				double rckcntrX = (rckxmin+rckxmax)/2;
				double rckcntrY = (rckymin+rckymax)/2;
				
				if( rckcntrX >= xminROI && 	rckcntrX <= xmaxROI &&
						rckcntrY >= yminROI && 	rckcntrY <= ymaxROI	) {
					fpCount++;
				}
			}			
		}
		
		return fpCount;
	}

	private static int checkDetected(HashMap<String, String> gtObj, ArrayList<HashMap<String, String>> rackInfoList) {
		boolean gotMatch = false;
		for(HashMap<String, String> rackObj:rackInfoList) {
			if(matchOnProduct(gtObj,rackObj)) {
				gotMatch = true;
				break;
			}
		}
		
		if(gotMatch) {
			return 1;
		}
		else {
			return 0;
		}		
	}
	
	private static int checkFalseDetected(HashMap<String, String> gtObj,
			ArrayList<HashMap<String, String>> rackInfoList) {
		int fpCount = 0;
		
		for(HashMap<String, String> rackObj:rackInfoList) {
			if(matchOnLocationMismatchOnProduct(gtObj,rackObj)) {
				fpCount++;
			}
		}		
		
		return fpCount;
	}	

	private static boolean matchOnProduct(HashMap<String, String> gtObj, HashMap<String, String> rackObj) {		
		if(rackObj.get("class").equals(gtObj.get("class"))) {
			//gt
			double gtWidth = Double.parseDouble(gtObj.get("width"));
			double gtHeight = Double.parseDouble(gtObj.get("height"));
			double gtxmin = Double.parseDouble(gtObj.get("xmin"));
			double gtymin = Double.parseDouble(gtObj.get("ymin"));
			double gtxmax = Double.parseDouble(gtObj.get("xmax"));
			double gtymax = Double.parseDouble(gtObj.get("ymax"));
			
			double gtcntrX = (gtxmin+gtxmax)/2;
			double gtcntrY = (gtymin+gtymax)/2;
			
			//rck
			double rckWidth = Double.parseDouble(rackObj.get("width"));
			double rckHeight = Double.parseDouble(rackObj.get("height"));
			
			double xResizeFactor = gtWidth/rckWidth;
			double yResizeFactor = gtHeight/rckHeight;
			
			double rckxmin = Double.parseDouble(rackObj.get("xmin"))*xResizeFactor;
			double rckymin = Double.parseDouble(rackObj.get("ymin"))*yResizeFactor;
			double rckxmax = Double.parseDouble(rackObj.get("xmax"))*xResizeFactor;
			double rckymax = Double.parseDouble(rackObj.get("ymax"))*yResizeFactor;
			
			double rckcntrX = (rckxmin+rckxmax)/2;
			double rckcntrY = (rckymin+rckymax)/2;
			
			//check center inclusion
			boolean matchFlag = false;
			if(gtcntrX >= rckxmin && gtcntrX <= rckxmax 
					&& gtcntrY >= rckymin && gtcntrY <= rckymax &&
			   rckcntrX >= gtxmin && rckcntrX <= gtxmax
			   		&& rckcntrY >= gtymin && rckcntrY <= gtymax					
					) {
				matchFlag = true;
			}
			
			//check intersection over union
			if(matchFlag) {
				double xA = Math.max(gtxmin, rckxmin);
				double yA = Math.max(gtymin, rckymin);
				
				double xB = Math.min(gtxmax, rckxmax);
				double yB = Math.min(gtymax, rckymax);
				
				if (((xB - xA + 1) > 0) && ((yB - yA + 1) > 0)) {
					double interArea = (xB - xA + 1) * (yB - yA + 1);

					double boxAArea = (gtxmax-gtxmin) * (gtymax-gtymin);
					double boxBArea = (rckxmax-rckxmin) * (rckymax-rckymin);

					double iou = interArea / (float) (boxAArea + boxBArea - interArea);
					
					if(iou > overlapThresh) {
						matchFlag = true;
						rackObj.put("matched", "Y");
					}
					else {
						matchFlag = false;
					}
				}
			}				
			
			return matchFlag;
		}
		else {
			return false;
		}		
	}

	private static boolean matchOnLocationMismatchOnProduct(HashMap<String, String> gtObj,
			HashMap<String, String> rackObj) {
		if(rackObj.get("class").equals(gtObj.get("class"))) {
			return false;
		}
		else {
			//gt
			double gtWidth = Double.parseDouble(gtObj.get("width"));
			double gtHeight = Double.parseDouble(gtObj.get("height"));
			double gtxmin = Double.parseDouble(gtObj.get("xmin"));
			double gtymin = Double.parseDouble(gtObj.get("ymin"));
			double gtxmax = Double.parseDouble(gtObj.get("xmax"));
			double gtymax = Double.parseDouble(gtObj.get("ymax"));
			
			double gtcntrX = (gtxmin+gtxmax)/2;
			double gtcntrY = (gtymin+gtymax)/2;
			
			//rck
			double rckWidth = Double.parseDouble(rackObj.get("width"));
			double rckHeight = Double.parseDouble(rackObj.get("height"));
			
			double xResizeFactor = gtWidth/rckWidth;
			double yResizeFactor = gtHeight/rckHeight;
			
			double rckxmin = Double.parseDouble(rackObj.get("xmin"))*xResizeFactor;
			double rckymin = Double.parseDouble(rackObj.get("ymin"))*yResizeFactor;
			double rckxmax = Double.parseDouble(rackObj.get("xmax"))*xResizeFactor;
			double rckymax = Double.parseDouble(rackObj.get("ymax"))*yResizeFactor;
			
			double rckcntrX = (rckxmin+rckxmax)/2;
			double rckcntrY = (rckymin+rckymax)/2;
			
			//check center inclusion
			boolean matchFlag = false;
			if(gtcntrX >= rckxmin && gtcntrX <= rckxmax 
					&& gtcntrY >= rckymin && gtcntrY <= rckymax &&
			   rckcntrX >= gtxmin && rckcntrX <= gtxmax
			   		&& rckcntrY >= gtymin && rckcntrY <= gtymax					
					) {
				matchFlag = true;
			}
			
			//check intersection over union
			if(matchFlag) {
				double xA = Math.max(gtxmin, rckxmin);
				double yA = Math.max(gtymin, rckymin);
				
				double xB = Math.min(gtxmax, rckxmax);
				double yB = Math.min(gtymax, rckymax);
				
				if (((xB - xA + 1) > 0) && ((yB - yA + 1) > 0)) {
					double interArea = (xB - xA + 1) * (yB - yA + 1);

					double boxAArea = (gtxmax-gtxmin) * (gtymax-gtymin);
					double boxBArea = (rckxmax-rckxmin) * (rckymax-rckymin);

					double iou = interArea / (float) (boxAArea + boxBArea - interArea);
					
					if(iou > overlapThresh) {
						matchFlag = true;
					}
					else {
						matchFlag = false;
					}
				}
			}				
			
			return matchFlag;
		}
	}
	
	private static void readFile(String fileFlag) {
		BufferedReader br = null;
		String line = "";
        String cvsSplitBy = ",";
        String fileName = "";
		try {
			if(fileFlag.equals("O")) {
				br = new BufferedReader(new FileReader(path+dataset+".csv"));
			}
			else {
				br = new BufferedReader(new FileReader(path+dataset+" Ground Truth.csv"));
			}
			
			boolean firstLine = true;
			 while ((line = br.readLine()) != null) {
				 if(firstLine) {
					 firstLine = false;
				 }
				 else {
					 String[] temp = line.split(cvsSplitBy);
					 fileName = temp[0];						 
					 HashMap<String,String> tempMap = new HashMap<String,String>();
					 tempMap.put("width", temp[1]);
					 tempMap.put("height", temp[2]);
					 tempMap.put("class", temp[3].replaceAll(dataset, ""));
					 tempMap.put("xmin", temp[4]);
					 tempMap.put("ymin", temp[5]);
					 tempMap.put("xmax", temp[6]);
					 tempMap.put("ymax", temp[7]);
					 
					 if(fileFlag.equals("O")) {
						 if(outputMap.containsKey(fileName)) {
							 outputMap.get(fileName).add(tempMap);
						 }
						 else {
							 ArrayList<HashMap<String,String>> newArr = new ArrayList<HashMap<String,String>>();
							 newArr.add(tempMap);
							 outputMap.put(fileName, newArr);
							 fileArray.add(fileName);
						 }	 
					 }
					 else {
						 if(gtMap.containsKey(fileName)) {
							 gtMap.get(fileName).add(tempMap);
						 }
						 else {
							 ArrayList<HashMap<String,String>> newArr = new ArrayList<HashMap<String,String>>();
							 newArr.add(tempMap);
							 gtMap.put(fileName, newArr);
						 }
					 }					 				 
				 }				 
			 }			
		} catch (IOException e) {
			e.printStackTrace();
		}		
	}	
}
