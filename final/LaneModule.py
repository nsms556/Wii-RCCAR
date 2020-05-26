from adafruit_servokit import ServoKit
import cv2
import Lane

kit = ServoKit(channels=16)

def steerTranslate(value) :
    trans = int(value * 4 / 3 - 10)

    return trans

def laneDeparture(frame) :
    steer = Lane.laneTracking(frame)
    if steer < 45 :
        steer = 45
    elif steer > 120 :
        steer = 120
            
    print('steer :', steer)
    kit.servo[0].angle = steerTranslate(steer)
