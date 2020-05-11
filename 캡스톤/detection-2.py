import cv2
import numpy as np
import imutils

template = cv2.imread('./30-2.png')
threshold = 0.9

def findTemplate(frame, template) :
    tplGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    tplCanny = cv2.Canny(tplGray, 50, 200)
    tplH, tplW = tplCanny.shape[:2]

    cv2.imshow('template', tplCanny)
    
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
    roi = frame[startY:endY, startX:endX]

    return frame, roi

def contourTracking(frame) :
    frameBlur = cv2.GaussianBlur(frame, (5,5), 0)
    frameYuv = cv2.cvtColor(frameBlur, cv2.COLOR_BGR2YUV)
    frameY, frameU, frameV = cv2.split(frameYuv)
    cannyU = cv2.Canny(frameU, 150, 255, apertureSize=3)
    cannyV = cv2.Canny(frameV, 50, 200, apertureSize=3)
    contoursU, _ = cv2.findContours(cannyU, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contoursV, _ = cv2.findContours(cannyV, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contoursV :
        (x, y, w, h) = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x,y), (x+w, y+h),(0,0,255),2)         

    return frame, cannyV

def signDetectCamera(video) :
    while True :
        s, frame = video.read()
        frame = cv2.resize(frame, (800,450))

        result, roi = findTemplate(frame, template)

        cv2.imshow('result', result)
        cv2.imshow('roi', roi)
        
        if cv2.waitKey(30) & 0xff == 27 :
            break;

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
            break;        

cam = cv2.VideoCapture(0)
vid = cv2.VideoCapture('./road.mp4')
if cam.isOpened() :
    cam.set(3, 640)
    cam.set(4, 360)

    signDetectCamera(cam)

    cam.release()
elif vid.isOpened() :
    signDetectVideo(vid)

    vid.release()
else :
    print("NoVideo")

cv2.destroyAllWindows()
