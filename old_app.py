import os
from flask import Flask, request, render_template, send_file, url_for
from werkzeug.utils import secure_filename
from src.core.ocr_processor import process_document, process_pdf, process_pdf_with_graphs
from src.utils.helpers import allowed_file
import logging

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
PROCESSED_FOLDER = os.path.join(STATIC_FOLDER, 'processed')

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error='Nenhum arquivo enviado')

        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error='Nenhum arquivo selecionado')

        if file and allowed_file(file.filename):
            try:
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                os.makedirs('static/graphs', exist_ok=True)

                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                if filename.lower().endswith('.pdf'):
                    content = process_pdf_with_graphs(filepath)
                    return render_template('result.html', content=content)
                else:
                    extracted_text = process_document(filepath)
                    return render_template('result.html',
                                           text=extracted_text,
                                           original_image=url_for('static', filename=filename))

            except Exception as e:
                logging.error(f"Error processing file: {str(e)}")
                return render_template('upload.html', error=f'Erro no processamento: {str(e)}')

        return render_template('upload.html', error='Tipo de arquivo não permitido')

    return render_template('upload.html')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    app.run(debug=True)
