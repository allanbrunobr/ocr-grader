from src.core.image_preprocessing.enhance import enhance_image, enhance_image_gray, desfoque_com_mediana
from src.core.image_preprocessing.threshold import apply_threshold, apply_otsu
from src.core.image_preprocessing.transform import resize_image, dilate_image, erode_image


def process_and_display_image(image):
    enhanced_gray = enhance_image_gray(image)
    dilated = dilate_image(enhanced_gray)
    erosed_in_dilated = resize_image(erode_image(dilated))
    return erosed_in_dilated  # or any other processed version that gives the best results
