import cv2
import numpy as np
import imutils
import pytesseract
from PIL import Image
import re

#pytesseract.pytesseract.tesseract_cmd = 'D:\School\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'
config = ('-l eng --oem 1 --psm 3')

template = cv2.imread('./object.png')
erodeK = np.ones((3,3), np.uint8)

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
            
    (_, Mloc, r) = found
    (startX, startY) = (int(Mloc[0] * r), int(Mloc[1] * r))
    (endX, endY) = (int((Mloc[0] + tplW) * r), int((Mloc[1] + tplH) * r))

    frame= cv2.rectangle(frame, (startX, startY), (endX, endY), (0,0,255), 2)
    roi = frame[startY:endY, startX:endX].copy()

    return frame, roi

def contourTracking(frame) :
    cont = frame.copy()
    contBlur = cv2.GaussianBlur(cont, (5,5), 0)
    contYuv = cv2.cvtColor(contBlur, cv2.COLOR_BGR2YUV)
    _ , _ , contV = cv2.split(contYuv)
    
    cannyV = cv2.Canny(contV, 50, 200, apertureSize=3)
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

def signDetectCamera(video) :
    while True :
        s, frame = video.read()
        
        contourRoi = contourTracking(frame)
        
        if contourRoi is not None :
            if contourRoi.shape[0] > 0 and contourRoi.shape[1] > 0 :

                result, roi = findTemplate(contourRoi, template)
                textY = int(result.shape[0] - 30)
                textX = int(result.shape[1] / 3)

                roi = cv2.GaussianBlur(roi, (3,3), 0)
                roiTH = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _ , roiTH = cv2.threshold(roiTH, 50,255, cv2.THRESH_BINARY)
                roiTH = cv2.erode(roiTH, erodeK, iterations=1)

                roiOCR = Image.fromarray(roiTH)
                text = pytesseract.image_to_string(roiOCR, config=config)

                print(text)
                cv2.putText(result, text, (textX, textY), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,127,127), 3)
                
                cv2.imshow('roi', roiTH)
                cv2.imshow('result', result)

        cv2.imshow('origin', frame)
        
        if cv2.waitKey(30) & 0xff == 27 :
            break

def signDetectVideo(video) :
    while True :
        if(video.get(cv2.CAP_PROP_POS_FRAMES) == video.get(cv2.CAP_PROP_FRAME_COUNT)) :
            video.open("./road.mp4")

        s, frame = video.read()
        frame = cv2.resize(frame, (1280,720))
        
        found = findTemplate(frame, template)
        
        if(found > 0) :
            frame, canny = contourTracking(frame)
            cv2.imshow('result', frame)
            cv2.imshow('canny', canny)
        else :
            cv2.imshow('result', frame)
        
        if cv2.waitKey(int(video.get(cv2.CAP_PROP_FPS))) & 0xff == 27 :
            break

cam = cv2.VideoCapture(0)
vid = cv2.VideoCapture('./road.mp4')
if cam.isOpened() :
    cam.set(3, 640)
    cam.set(4, 480)

    try :
        signDetectCamera(cam)
    finally :
        cam.release()
        
elif vid.isOpened() :
    signDetectVideo(vid)

    vid.release()
else :
    print("NoVideo")

cv2.destroyAllWindows()
