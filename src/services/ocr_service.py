import cv2
import numpy as np
from PIL import Image
from google.cloud import vision
import io
import json
from pdf2image import convert_from_path
from src.core.image_preprocessing.processor import process_and_display_image

def detect_text_with_coordinates(image_path):
    client = vision.ImageAnnotatorClient()
    google_ocr_dict = {}

    image = cv2.imread(image_path)
    _, img_encoded = cv2.imencode('.png', process_and_display_image(image))
    content = img_encoded.tobytes()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    text_num = 0
    for text in texts:
        google_ocr_dict[text_num] = {}
        vertices = [[vertex.x, vertex.y] for vertex in text.bounding_poly.vertices]
        google_ocr_dict[text_num]['text'] = text.description
        google_ocr_dict[text_num]['coords'] = vertices
        text_num += 1

    output_filename = f"processed_image_new_{os.path.basename(image_path)}.json"
    with open(output_filename, "w") as json_file:
        json.dump(google_ocr_dict, json_file, indent=4)

    print(f"Created {output_filename} using Google OCR")
    return google_ocr_dict[0]["text"].replace("\n", " ")

def detect_text_in_pdf(pdf_path, filename):
    client = vision.ImageAnnotatorClient()
    text_results = []

    pages = convert_from_path(pdf_path)
    for page_number, page in enumerate(pages, 1):
        opencv_image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
        processed_image = process_and_display_image(opencv_image)
        processed_pil = Image.fromarray(processed_image)

        img_byte_arr = io.BytesIO()
        processed_pil.save(img_byte_arr, format='PNG')
        content = img_byte_arr.getvalue()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            text_results.append({
                'filename': filename,
                'page': page_number,
                'text_data': texts[0].description
            })

    return text_results
