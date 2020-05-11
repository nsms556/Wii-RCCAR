import cv2
import numpy as np
import random

template = cv2.imread('./30.png')

threshold = 0.6

cam = cv2.VideoCapture(0)

surf = cv2.xfeatures2d.SURF_create()
bfMatch = cv2.BFMatcher()

if cam.isOpened() :
    cam.set(3, 640)
    cam.set(4, 360)

    while True :
        s, frame = video.read()

        frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        temW, temH = templateGray.shape[::-1]
        keyList, keyDiscriptor = surf.detectAndCompute(frameGray, None)
        temList, temDiscriptor = surf.detectAndCompute(templateGray, None)
        
        matchList = bfMatch.knnMatch(keyDiscriptor, temDiscriptor, k=2)

        good = []

        for m, n in matchList :
            if m.distance < 0.4 * n.distance :
                good.append([m])

        random.shuffle(good)

        match = cv2.drawMatchesKnn(frame, keyList, template, temList, good[:30], flags=2, outImg=None)

        cv2.imshow('match', match)
        cv2.waitKey()
        cv2.destroyAllWindows()
        

        
        

    cam.release()
else :
    print("NoVideo")

cv2.destroyAllWindows()
