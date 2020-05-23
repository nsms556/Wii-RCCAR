import cv2
import numpy as np

template = cv2.imread('./30-4.png', 0)
temW, temH = template.shape[::-1]
threshold = 0.6

def findTemplate(frame, template) :
    frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    res = cv2.matchTemplate(frameGray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    cv2.imshow('match', res)

    return len(loc[0])

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
        #frame = cv2.resize(frame, (1280,720))
        
        found = findTemplate(frame, template)
        
        if(found > 0) :
            frame, canny = contourTracking(frame)
            cv2.imshow('result', frame)
            cv2.imshow('canny', canny)
        else :
            cv2.imshow('result', frame)
        
        if cv2.waitKey(30) & 0xff == 27 :
            break;

def signDetectVideo(video) :
    while True :
        if(video.get(cv2.CAP_PROP_POS_FRAMES) == video.get(cv2.CAP_PROP_FRAME_COUNT)):
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
