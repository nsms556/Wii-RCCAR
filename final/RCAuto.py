print('Wating For Module')

import cv2
import LaneModule, ObjectModule
#import WaveModule
from time import sleep

print('Waiting For Camera')

def gstreamer_pipeline(
    capture_width=640,
    capture_height=360,
    display_width=640,
    display_height=360,
    framerate=30,
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

def printCarStatus(text, speed) :
    if text == '30' :
        print('Max Speed Limit : 30')
    elif text == '50' :
        print('Max Speed Limit : 50')
    else :
        print('Car Speed :', speed)

def speedUp(speed, maxSpeed) :
    if speed > maxSpeed :
        newSpeed = speed - 1
    elif speed + 0.5 >= maxSpeed :
        newSpeed = maxSpeed
    elif speed + 0.5 < maxSpeed :
        newSpeed = speed + 0.5
    
    return newSpeed
        
def maxSpeedLimit(text) :
    ret = None
    if text == '30' :
        ret = 30
    elif text == '50' :
        ret = 50
    return ret

cam = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

if cam.isOpened() :
    capTime = 31
    nowSpeed = 0
    maxSpeed = 50
    forDis = 0
    try :
        while True :
            textObject = None
            ret, frame = cam.read()
            
            LaneModule.laneDeparture(frame)
            if capTime > 30 :
                capTime = 0
                textObject = ObjectModule.findObject(frame)
            #forDis = WaveModule.disMeasure()
            
            cv2.imshow('origin', frame)

            if textObject == 'STOP' or textObject == '5TOP' or textObject == 'CTOP' or textObject == 'ST0P' :
                print('Car Stop 5 Seconds')
                nowSpeed = 0
                sleep(5)
            elif textObject != None :
                tmp = maxSpeedLimit(textObject)
                if tmp != None :
                    maxSpeed = tmp
            
            printCarStatus(textObject, nowSpeed)
            nowSpeed = speedUp(nowSpeed, maxSpeed)

            #forDis = WaveModule.disMeasure()
            #print('Forward Distance :', forDis)
            
            capTime += 1
            if cv2.waitKey(30) & 0xff == 27 :
                break
    except Exception as e :
        print(e)
    finally :
        cv2.destroyAllWindows()
        cam.release()
else :
    print('NoVideo')
