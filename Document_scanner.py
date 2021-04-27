from transform.pyimagesearch import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils

def showIMG(image,name):
    cv2.imshow(name,image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

ap =  argparse.ArgumentParser()
ap.add_argument("-i","--image",required = True, help = "Path to the image to be scanned")
args = vars(ap.parse_args())

# load the image and compute the ratio of image height
# new height, clone it, and resize it
image = cv2.imread(args["image"])
ratio = image.shape[0] / 500.0
orig = image.copy()
image = imutils.resize(image, height = 500)

# convert the image to grayscale, blur it, and find edges
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)

# show the original image and edge detected image
print("STEP 1: Edge Detection")
cv2.imshow("Image", image)
cv2.imshow("Edged", edged)
cv2.waitKey(1)
cv2.destroyAllWindows()

# find the contours in the edged image, keeping only largest ones
#initialize the screen contour
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

# loop over the contours
for c in cnts:
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	# if our approximated contour has four points, then we can assume that we have found our screen
	if len(approx) == 4:
		screenCnt = approx
		break

# show the outline of the piece of paper
print("STEP 2: Find contours of paper")
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("Outline", image)
cv2.waitKey(1)
cv2.destroyAllWindows()

# apply the four point transform to obtain a top-down view
warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

# convert the warped image to grayscale, then threshold it
# to give it that 'black and white' paper effect
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
T = threshold_local(warped, 11, offset = 10, method = "gaussian")
warped = (warped > T).astype("uint8") * 255

# show the scanned images and save it 
print("STEP 3: Apply perspective transform")
showIMG(imutils.resize(warped,height=650),"Scanned Image")
opname="output_"+args["image"].split("/")[-1]
cv2.imwrite(opname,warped)