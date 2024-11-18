from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from src.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, UPLOAD_HTML
from src.services.ocr_service import detect_text_with_coordinates, detect_text_in_pdf
from src.services.chatgpt_service import send_to_chatgpt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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

            if filename.lower().endswith('.pdf'):
                results = detect_text_in_pdf(filepath, filename)
            else:
                text = detect_text_with_coordinates(filepath)
                results = [{'filename': filename, 'text_data': text}]

            chatgpt_analysis = send_to_chatgpt(results)
            return render_template('result.html', results=results, analysis=chatgpt_analysis)

    return render_template(UPLOAD_HTML)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
