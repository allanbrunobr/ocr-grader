import cv2
import numpy as np


def resize_image(image):
    resized = cv2.resize(image, None, fx=1.5, fy = 1.5, interpolation=cv2.INTER_CUBIC)
    return resized

def erode_image(image):
    kernel = np.ones((1, 1), np.uint8)
    eroded = cv2.erode(image, kernel, iterations=5)
    return eroded

def dilate_image(image):
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(image, kernel, iterations=5)
    return dilated