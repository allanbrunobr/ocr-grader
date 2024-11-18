import cv2

def apply_threshold(image):
    thresh = cv2.threshold(image, 105, 255, cv2.THRESH_BINARY)
    return thresh


def apply_adaptive_threshold(image):
    thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 9)
    return thresh


def apply_threshold(image):
    thresh = cv2.threshold(image, 105, 255, cv2.THRESH_BINARY)
    return thresh

def apply_otsu(image):
    val, otsu = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    print(val)
    return otsu

def apply_adaptive_media_glauss(image):
    thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 9)
    return thresh