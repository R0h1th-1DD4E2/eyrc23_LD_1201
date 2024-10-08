'''
# Team ID:          < TLD#1201 >
# Theme:            < Luminosity Drone (LD) >
# Author List:      < Rolwin Cardoza, Rohith Vishnu Achari >
# Filename:         < LD_1201_led_detection.py >
# Functions:        <  >
# Global variables: <  >
'''

# import the necessary packages
from imutils import contours
from skimage import measure
import numpy as np
import imutils
import cv2

# load the image
image = cv2.imread('led.jpg', 1)

# convert it to grayscale, and blur it
gray_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred_image = cv2.GaussianBlur(gray_scale, (11, 11), 0)

# threshold the image to reveal light regions in the blurred image
threshold = cv2.threshold(blurred_image, 175, 195, cv2.THRESH_BINARY)[1]

# perform a series of erosions and dilations to remove any small blobs of noise from the thresholded image
threshold = cv2.erode(threshold, None, iterations=2)
threshold = cv2.dilate(threshold, None, iterations=4)

# perform a connected component analysis on the thresholded image
labels = measure.label(threshold, connectivity=2, background=0)
mask = np.zeros(threshold.shape, dtype="uint8")

# loop over the unique components
for label in np.unique(labels):
    # if this is the background label, ignore it
    if label == 0:
        continue

    # otherwise, construct the label mask and count the number of pixels 
    labelMask = np.zeros(threshold.shape, dtype="uint8")
    labelMask[labels == label] = 255
    numPixels = cv2.countNonZero(labelMask)

    # if the number of pixels in the component is sufficiently large, then add it to our mask of "large blobs"
    if numPixels > 300:
        mask = cv2.add(mask, labelMask)

# find the contours in the mask, then sort them from left to right
cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = contours.sort_contours(cnts)[0]

# Initialize lists to store centroid coordinates and area
centroids = []
areas = []

# Loop over the contours
for i, c in enumerate(cnts):
    # Calculate the area of the contour
    area = cv2.contourArea(c)

    # Filter out small contours
    if area > 300:
        # Compute the centroid of the contour
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0

        # Append centroid coordinates and area to the respective lists
        centroids.append((cX, cY))
        areas.append(area)

        # Draw the bright spot on the image
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv2.putText(image,f"LED {i+1}",(cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0),2)

# Save the output image as a PNG file
cv2.imwrite("led_detection_results.png", image)

# Open a text file for writing
with open("led_detection_results.txt", "w") as file:
    # Write the number of LEDs detected to the file
    file.write(f"No. of LEDs detected: {len(centroids)}\n")
    # Loop over the centroids and areas
    for i, (cX, cY) in enumerate(centroids):
        file.write(f"Centroid #{i + 1}: ({cX}, {cY})\nArea #{i + 1}: {areas[i]}\n")
# Close the text file
file.close()
