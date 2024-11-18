import cv2
import numpy as np
from PIL import Image
from flask import Flask, render_template, request
from google.cloud import vision
import os
import io
import json

from openai import OpenAI
from pdf2image import convert_from_path
from typing import List, Dict

from werkzeug.utils import secure_filename

from src.core.image_preprocessing.processor import process_and_display_image

UPLOAD_HTML = 'upload.html'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

client = OpenAI()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials/credentials.json'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template(UPLOAD_HTML, error='No file uploaded')

        file = request.files['file']
        if file.filename == '':
            return render_template(UPLOAD_HTML, error='No file selected')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the file
            if filename.lower().endswith('.pdf'):
                results = detect_text_in_pdf(filepath, filename)
            else:
                text = detect_text_with_coordinates(filepath)
                results = [{'filename': filename, 'text_data': text}]

            # Get ChatGPT analysis
            chatgpt_analysis = send_to_chatgpt(results)

            return render_template('result.html',
                                   results=results,
                                   analysis=chatgpt_analysis)

    return render_template(UPLOAD_HTML)
def detect_text_with_coordinates(image_path):
    client = vision.ImageAnnotatorClient()
    google_ocr_dict = {}

    # Read image and enhance quality
    image = cv2.imread(image_path)
    # Convert enhanced image to bytes
    _, img_encoded = cv2.imencode('.png', process_and_display_image(image))
    content = img_encoded.tobytes()

    # Process with Google Vision
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

    # Convert PDF pages to images
    pages = convert_from_path(pdf_path)

    for page_number, page in enumerate(pages, 1):
        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
        processed_image = process_and_display_image(opencv_image)
        processed_pil = Image.fromarray(processed_image)

        # Enhance contrastConvert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        processed_pil.save(img_byte_arr, format='PNG')
        content = img_byte_arr.getvalue()

        # Create image object
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

def send_to_chatgpt(text_results: List[Dict]) -> str:
    prompt = "Aqui está o conteúdo da prova extraído via OCR:\n\n"
    for result in text_results:
        if 'page' in result:
            prompt += f"Documento: {result['filename']}\n"
            prompt += f"Página {result['page']}:\n{result['text_data']}\n\n"
        else:
            prompt += f"Documento: {result['filename']}\n{result['text_data']}\n\n"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """Você é um professor experiente e vai analisar esta prova.
            
            Suas responsabilidades são:
            1. Identifique cada questão pelo seu cabeçalho/enunciado
            2. Para cada questão identificada:
               - Apresente o cabeçalho/enunciado original
               - Se não respondida: forneça a resposta correta com explicação
               - Se respondida: indique se está certa ou errada
               - Para questões erradas: explique o erro e forneça a resposta correta
            3. Atribua uma nota final considerando o desempenho geral
            
            Formato da sua resposta para cada questão:
            === QUESTÃO X (cabeçalho original) ===
            - Status: [Respondida/Não respondida]
            - Avaliação: [Correta/Incorreta/Resposta sugerida]
            - Explicação detalhada
            - Resposta correta (quando aplicável)
            
            Ao final:
            - Nota final
            - Feedback construtivo"""},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)