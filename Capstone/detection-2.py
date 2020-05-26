import cv2
import numpy as np
import imutils
import pytesseract
import time
from PIL import Image
import re

#pytesseract.pytesseract.tesseract_cmd = 'D:\School\Tesseract-OCR\\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
config = ('-l eng --oem 1 --psm 3')

template = cv2.imread('./Object.png')
erodeK = np.ones((3,3), np.uint8)
capSecond = 2
delayTime = 40
capPeriod = 1000 / delayTime * capSecond
objNum = 0

def gstreamer_pipeline(
    capture_width=800,
    capture_height=450,
    display_width=800,
    display_height=450,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def objNumIncrement() :
    global objNum

    objNum += 1

    if objNum > 9 :
        objNum = 0

def findTemplate(frame, template) :
    tplGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    tplCanny = cv2.Canny(tplGray, 50, 200)
    tplH, tplW = tplCanny.shape[:2]
    
    frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found = None

    for scale in np.linspace(0.2, 1.0, 20)[::-1] :
        frameResized = imutils.resize(frameGray, width = int(frameGray.shape[1] * scale))
        r = frameGray.shape[1] / float(frameResized.shape[1])

        if frameResized.shape[0] < tplH or frameResized.shape[1] < tplW :
            break

        frameCanny = cv2.Canny(frameResized, 50, 200)
        result = cv2.matchTemplate(frameCanny, tplCanny, cv2.TM_CCOEFF_NORMED)

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
    cont = frame.copy()
    cont = cv2.GaussianBlur(cont, (5,5), 0)
    cont = cv2.cvtColor(cont, cv2.COLOR_BGR2YUV)
    _ , _ , contV = cv2.split(cont)
    
    low, high = getCannyValue(frame)

    cannyV = cv2.Canny(contV, low, high, apertureSize=3)
    contoursV, _ = cv2.findContours(cannyV, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
    roi = cv2.GaussianBlur(roi, (3,3), 0)
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _ , roi = cv2.threshold(roi, 50,255, cv2.THRESH_BINARY)
    roi = cv2.erode(roi, erodeK, iterations=1)

    objWriteName = './ObjDetect/obj' + str(objNum) + '.jpg'
    cv2.imwrite(objWriteName, roi)

    return roi

def findCharacter(ocrImage) :
    objReadName = './ObjDetect/obj' + str(objNum) + '.jpg'
    roiOCR = Image.open(objReadName)
    objNumIncrement()

    text = pytesseract.image_to_string(roiOCR, config=config)

    return text
   
def signDetectCamera(video) :
    capTime = 81
    while True :
        s, frame = video.read()

        contourRoi = contourTracking(frame)
        
        if contourRoi is not None :
            if contourRoi.shape[0] > 0 and contourRoi.shape[1] > 0 :
                result, roi = findTemplate(contourRoi, template)
            
                if result is not None and roi is not None and capTime > capPeriod :
                    capTime = 0
                    preOCR = preProcessToOCR(roi)
                    
                    text = findCharacter(preOCR)
                    cv2.putText(result, text, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,127,127), 3)
                    
                    cv2.imshow('roi', preOCR)
                    cv2.imshow('result', result)

        cv2.imshow('origin', frame)
        
        if cv2.waitKey(delayTime) & 0xff == 27 :
            break
        capTime += 1

cam = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
if cam.isOpened() :
    try :
        signDetectCamera(cam)
    finally :
        cam.release()
        cv2.destroyAllWindows()
else :
    print("NoVideo")
