import os

import re
import pytesseract
from PIL import Image
import cv2
import logging
import numpy as np
from pdf2image import convert_from_path
import easyocr
import PyPDF2
import io

easyocr_reader = easyocr.Reader(['pt', 'en'], gpu=False)

def extract_graph_text_with_easyocr(image):
    try:
        result = easyocr_reader.readtext(image, detail=0, paragraph=True)
        text = "\n".join(result)
        return text.replace('%', '%%') if text else ""
    except Exception as e:
        logging.error(f"Erro no EasyOCR: {e}")
        return ""


def process_pdf_with_content(pdf_path):
    pages = convert_from_path(pdf_path)
    content = []

    for page_number, page in enumerate(pages, 1):
        # Convert page to OpenCV format
        page_np = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)

        # Detect all content types
        page_content = detect_content(page_np)

        # Process regular text
        text = process_document_from_array(page_np)

        # Save detected content
        content.append({
            'page_number': page_number,
            'text': text,
            'graphs': page_content['graphs'],
            'equations': page_content['equations'],
            'statistical_charts': page_content['statistical_charts']
        })

    return content

def preprocess_document(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # Remove noise
    denoised = cv2.fastNlMeansDenoising(enhanced)

    # Adaptive thresholding for better text extraction
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 21, 11
    )

    return thresh
def process_pdf(pdf_path):
    # Convert PDF to images
    pages = convert_from_path(pdf_path)
    text_content = []

    for page_number, page in enumerate(pages, 1):
        # Convert page to numpy array for OpenCV processing
        page_np = np.array(page)

        # Process the page image
        processed = preprocess_document(page_np)

        # OCR configuration for Portuguese
        custom_config = r'--oem 3 --psm 3 -l por'

        # Extract text from the page
        text = pytesseract.image_to_string(
            Image.fromarray(processed),
            config=custom_config,
            lang='por'
        )

        text_content.append(f"Página {page_number}:\n{text}\n")

    return "\n".join(text_content)

def process_document(image_path):
    # Read image
    image = cv2.imread(image_path)

    # Preprocess
    processed = preprocess_document(image)
    custom_config = r'--oem 3 --psm 3 -l por+por_best'

    pil_image = Image.fromarray(processed)

    text = pytesseract.image_to_string(
        pil_image,
        config=custom_config,
        lang='por'
    )

    return text


def process_pdf_with_graphs(pdf_path):
    try:
        pages = convert_from_path(pdf_path)
        content = []

        for page_number, page in enumerate(pages, 1):
            page_np = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
            graphs = detect_graphs(page_np)

            # Process text on the page
            text = process_document_from_array(page_np)
            logging.debug(f"Texto extraído da página {page_number}: {text}")

            if text:
                # Escapar porcentagem para evitar erros
                text = text.replace('%', '%%')

            graph_paths = []
            graph_texts = []

            for i, graph_data in enumerate(graphs):
                graph_text = extract_graph_text_with_easyocr(graph_data['image'])
                logging.debug(f"Texto extraído do gráfico {i} na página {page_number}: {graph_text}")

                if graph_text:
                    graph_text = graph_text.replace('%', '%%')
                graph_texts.append(graph_text)

            content.append({
                'page_number': page_number,
                'text': text,
                'graphs': graph_paths,
                'graph_texts': graph_texts
            })

        return content

    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return []


def process_document_from_array(image_array):
    try:
        processed = preprocess_document(image_array)
        custom_config = r'--oem 3 --psm 3 -l por'
        text = pytesseract.image_to_string(processed, config=custom_config, lang='por')
        logging.debug(f"Texto extraído do documento: {text}")

        # Escapar '%' para evitar problemas posteriores
        return text.replace('%', '%%') if text else ""
    except Exception as e:
        logging.error(f"Erro ao processar documento: {e}")
        return ""


def detect_graphs(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    graphs = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h

        # Expanded criteria for different graph types
        if (area > 8000 and  # Reduced minimum area
                0.3 <= aspect_ratio <= 3.0 and  # Wider range for various graph types
                y > image.shape[0] * 0.15):

            # Larger padding for capturing axis labels and titles
            padding_x = int(w * 0.2)
            padding_y = int(h * 0.25)  # Extra padding for title

            y1 = max(0, y - padding_y)
            y2 = min(image.shape[0], y + h + padding_y)
            x1 = max(0, x - padding_x)
            x2 = min(image.shape[1], x + w + padding_x)

            graph_region = image[y1:y2, x1:x2]

            # Check for graph characteristics (bars, axes, labels)
            if is_statistical_graph(graph_region):
                graphs.append({
                    'image': graph_region,
                    'type': 'statistical',
                    'text': extract_graph_text(graph_region)
                })

    return graphs

def is_statistical_graph(image):
    # Detect horizontal/vertical lines (axes)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=20, maxLineGap=10)

    # Check for vertical lines (bars)
    if lines is not None:
        vertical_lines = sum(1 for line in lines if abs(line[0][3] - line[0][1]) > abs(line[0][2] - line[0][0]))
        if vertical_lines > 3:  # At least 3 vertical lines for bar charts
            text = pytesseract.image_to_string(image, config='--psm 6')
            return any(char.isdigit() for char in text)

    return False


def extract_graph_text(image):
    """Retorna texto de gráficos, usando EasyOCR como alternativa."""
    try:
        text = extract_graph_text_with_easyocr(image)  # EasyOCR para gráficos
        if text.strip():
            return text
    except Exception as e:
        logging.error(f"Erro ao processar gráfico com EasyOCR: {e}")

    # Retorna fallback com Tesseract se EasyOCR falhar
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, config=config, lang='por')


def detect_content(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    content = {
        'graphs': [],
        'equations': [],
        'statistical_charts': []
    }

    # First pass: detect larger regions for graphs
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)

        # Larger minimum area for graphs
        if area > 15000:
            region = image[y:y+h, x:x+w]

            # Enhanced statistical chart detection
            if is_statistical_chart(region):
                padding = int(h * 0.4)  # Increased padding
                chart_region = extract_with_padding(image, x, y, w, h, padding)
                content['statistical_charts'].append(chart_region)

    # Second pass: detect equations with different criteria
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)

        # Specific criteria for equations
        if 1000 < area < 15000 and 2 < w/h < 10:
            region = image[y:y+h, x:x+w]
            if is_equation(region):
                eq_text = extract_equation(region)
                if eq_text:
                    content['equations'].append(eq_text)

    return content


def is_equation(region):
    # Enhanced equation detection
    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789xy+=;()- '
    text = pytesseract.image_to_string(region, config=config)

    # More comprehensive patterns
    equation_patterns = [
        r'\d+[xy]',  # Coefficients with variables
        r'[xy]\s*[+\-=]',  # Variables with operators
        r'=\s*\d+',  # Equals followed by number
        r'[+\-=]\s*\d+[xy]'  # Operators with coefficients
    ]

    return any(re.search(pattern, text, re.IGNORECASE) for pattern in equation_patterns)

def is_statistical_chart(region):
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # More sensitive line detection
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, minLineLength=20, maxLineGap=10)

    # Check for vertical lines (bars)
    if lines is not None:
        vertical_lines = sum(1 for line in lines if abs(line[0][3] - line[0][1]) > abs(line[0][2] - line[0][0]))
        if vertical_lines > 3:  # At least 3 vertical lines for bar charts
            text = pytesseract.image_to_string(region, config='--psm 6')
            return any(char.isdigit() for char in text)

    return False

def extract_with_padding(image, x, y, w, h, padding):
    height, width = image.shape[:2]

    # Calculate padded coordinates
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width, x + w + padding)
    y2 = min(height, y + h + padding)

    return image[y1:y2, x1:x2]

def extract_equation(image):
    # Special config for mathematical equations
    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789xy+=;()'
    text = pytesseract.image_to_string(image, config=config)

    # Format equations nicely
    if text:
        equations = text.split(';')
        return '; '.join(eq.strip() for eq in equations if eq.strip())