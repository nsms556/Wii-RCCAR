import cv2
import numpy as np
from matplotlib import pyplot as plt

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 360)

template = cv2.imread('./noleft.png',0)

if not cap.isOpened() :
    print("NoCamera")
    
elif template is None :
    print("NoTemplate")
    
else :
    while True :
        ret, frame = cap.read()
        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(frameGray,template,cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
 
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
 
        cv2.rectangle(frame,top_left, bottom_right, 255, 2)
        
        cv2.imshow('test', frame)
        cv2.imshow('match', res)

        k = cv2.waitKey(1)
        if k == 27 :
            break

    cap.release()

    cv2.destroyAllWindows()
