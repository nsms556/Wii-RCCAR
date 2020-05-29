import cv2
import numpy as np
import imutils
import pytesseract
from PIL import Image
import re

config = ('-l eng --oem 1 --psm 3')
template = cv2.imread('/home/gaonnuri/workspace/Wii-RCCAR/final/img/Object.png')
erodeK = np.ones((3,3), np.uint8)
capPeriod = 25
objNum = 0
capTime = 51

tmGPU = cv2.cuda.createTemplateMatching(16, cv2.TM_CCOEFF_NORMED)
gaussian5 = cv2.cuda.createGaussianFilter(16, 16, (5,5), 0)
gaussian3 = cv2.cuda.createGaussianFilter(16, 16, (3,3), 0)

def objNumIncrement() :
    global objNum

    objNum += 1

    if objNum > 9 :
        objNum = 0

def findTemplate(frame, template) :
    tplGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    tplCanny = cv2.Canny(tplGray, 50, 200)
    tplCannyGPU = cv2.cuda_GpuMat(tplCanny)
    tplH, tplW = tplCanny.shape[:2]
    
    frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    
    found = None
    
    for scale in np.linspace(0.2, 1.0, 20)[::-1] :
        frameResized = imutils.resize(frameGray, width = int(frameGray.shape[1] * scale))
        r = frameGray.shape[1] / float(frameResized.shape[1])

        if frameResized.shape[0] < tplH or frameResized.shape[1] < tplW :
            break

        frameCanny = cv2.Canny(frameResized, 50, 200)
        frameCannyGPU = cv2.cuda_GpuMat(frameCanny)
        
        resultGPU = tmGPU.match(frameCannyGPU, tplCannyGPU)
        result = resultGPU.download()
        (_, Mval, _, Mloc) = cv2.minMaxLoc(result)

        if found is None or Mval > found[0] :
            found = (Mval, Mloc, r)
    
    if found is not None :
        (_, Mloc, r) = found
        (startX, startY) = (int(Mloc[0] * r), int(Mloc[1] * r))
        (endX, endY) = (int((Mloc[0] + tplW) * r), int((Mloc[1] + tplH) * r))

        frame = cv2.rectangle(frame, (startX, startY), (endX, endY), (0,0,255), 2)
        roi = frame[startY:endY, startX:endX].copy()    
    else :
        frame = None
        roi = None

    return frame, roi

def getCannyValue(frame, sigma = 0.23) :
    median = np.median(frame) 

    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))

    return lower, upper

def contourTracking(frame) :
    contGPU = cv2.cuda_GpuMat(frame)
    contFilterGPU = gaussian5.apply(contGPU)
    contYuvGPU = cv2.cuda.cvtColor(contFilterGPU, cv2.COLOR_BGR2YUV)
    _, _, vContGPU = cv2.cuda.split(contYuvGPU)
    contV = vContGPU.download()

    low, high = getCannyValue(frame)

    cannyV = cv2.Canny(contV, low, high, apertureSize=3)
    contoursV, _ = cv2.findContours(cannyV, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cv2.imshow('a', contV)
    cv2.imshow('b', cannyV)
    
    if len(contoursV) != 0 :
        squareList = []
        areaList = []
        for cnt in contoursV:
            square = cv2.boundingRect(cnt)
            squareList.append(square)
        
        for sq in squareList :
            area = sq[2] * sq[3]
            areaList.append(area)

        npAreaList = np.array(areaList)
        maxArea = np.argmax(npAreaList)

        (x, y, w, h) = squareList[maxArea]

        stX = int(y - (h / 2))
        stY = int(x - (w / 2))
        endX = int((y + h) + (h / 2))
        endY = int((x + w) + (w / 2))
        ret = frame[stX:endX, stY:endY].copy()
    else :
        ret = None

    return ret

def preProcessToOCR(roi) :
    roiGPU = cv2.cuda_GpuMat(roi)
    roiFilterGPU = gaussian3.apply(roiGPU)
    roiGrayGPU = cv2.cuda.cvtColor(roiFilterGPU, cv2.COLOR_BGR2GRAY)
    _, roiTHGPU = cv2.cuda.threshold(roiGrayGPU, 75, 255, cv2.THRESH_BINARY)
    roi = roiTHGPU.download()
    roi = cv2.erode(roi, erodeK, iterations=1)

    objWriteName = '/home/gaonnuri/workspace/Wii-RCCAR/final/ObjDetect/obj' + str(objNum) + '.jpg'
    
    cv2.imwrite(objWriteName, roi)

    return roi

def findCharacter(ocrImage) :
    objReadName = '/home/gaonnuri/workspace/Wii-RCCAR/final/ObjDetect/obj' + str(objNum) + '.jpg'
    roiOCR = Image.open(objReadName)
    objNumIncrement()

    text = pytesseract.image_to_string(roiOCR, config=config)

    return text
   
def findObject(frame) :
    contourRoi = contourTracking(frame)
    
    if contourRoi is not None :
        if contourRoi.shape[0] > 0 and contourRoi.shape[1] > 0 :
            result, roi = findTemplate(contourRoi, template)

            if result is not None and roi is not None :
                preOCR = preProcessToOCR(roi)

                text = findCharacter(preOCR)
                text = text.upper()
                text = text.replace(' ', '')
                cv2.putText(result, text, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,127,127), 3)
                
                cv2.imshow('roi', preOCR)
                cv2.imshow('result', result)

                return text
