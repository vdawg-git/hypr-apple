import cv2
import os
import numpy as np

# Nessecary for show image to work
os.environ["QT_QPA_PLATFORM"] = "xcb"

baseFrame = 'frames/00131.png'
blackFrame = 'frames/06413.png'

img = cv2.imread(blackFrame, cv2.IMREAD_REDUCED_GRAYSCALE_4)
img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)[1]

# Lets make masking easier and always have more white than black pixels
# Create a boolean mask for black pixels
imgUint8 = img.astype(np.uint8)
blackMask = imgUint8 == 0
blackPixels = np.sum(blackMask)
whitePixels = np.sum(~blackMask)
if blackPixels > whitePixels:
    img = cv2.bitwise_not(img)

cv2.imshow('result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()


