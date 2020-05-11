import cv2
import numpy as np
from matplotlib import pyplot as plt
 
img = cv2.imread('./test.png')
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
templateOrigin = cv2.imread('./limit30.jpg',0)
locList = []
sizeList = []
threshold = 0.9

# Apply template Matching
for i in range(3) :
    ratio = 0.5 * i + 0.5
    template = cv2.resize(templateOrigin, dsize=(0,0), fx = ratio, fy=ratio, interpolation=cv2.INTER_LINEAR)
    w, h = template.shape[::-1]
    sizeList.append((w,h))
    res = cv2.matchTemplate(imgGray,template,cv2.TM_CCOEFF_NORMED)
    locList.append(np.where(res>= threshold))

for i in range(3) :    
    for pt in zip(*locList[i][::-1]) :
        cv2.rectangle(img, pt, (pt[0] + sizeList[i][0], pt[1] + sizeList[i][1]), (255,0,0), 2)

cv2.imshow('result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
