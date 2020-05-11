import cv2
import numpy as np
from matplotlib import pyplot as plt
 
img = cv2.imread('./test.png')
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
template = cv2.imread('./noleft.png',0)
template2 = cv2.resize(template, dsize = (0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
threshold = 0.9
w, h = template.shape[::-1]
w2, h2 = template2.shape[::-1]
# Apply template Matching
res = cv2.matchTemplate(imgGray,template,cv2.TM_CCOEFF_NORMED)
res2 = cv2.matchTemplate(imgGray,template2, cv2.TM_CCOEFF_NORMED)

loc = np.where(res >= threshold)
loc2 = np.where(res2 >= threshold)
for pt in zip(*loc[::-1]):
    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (255,0,0), 2)
for pt in zip(*loc2[::-1]):
    cv2.rectangle(img, pt, (pt[0] + w2, pt[1] + h2), (255,0,0), 2)
 
cv2.imshow('result', img)
cv2.imshow('match', res)
cv2.waitKey(0)
cv2.destroyAllWindows()
