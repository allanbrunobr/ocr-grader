from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from src.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, UPLOAD_HTML
from src.services.ocr_service import detect_text_in_pdf, detect_text_with_coordinates
from src.services.chatgpt_service import send_to_chatgpt
from src.core.audio_processing.podcast_template import generate_conversation
from src.core.audio_processing.audio_podcast import generate_conversation_audios, combine_audio_files

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

            person1 = "Professor" #Host1
            person2 = "Aluno"
            conversation = generate_conversation(chatgpt_analysis,person1,person2)

            audio_dir = os.path.join(app.static_folder, 'audio')
            os.makedirs(audio_dir, exist_ok=True)

            person1_voice_id = 'Bl2Yq4M5mRgYR84bggeP' # Kuhcsal
            person2_voice_id = 'MZxV5lN3cv7hi1376O0m' # Ana Dias

            audio_files = generate_conversation_audios(
                conversation,
                person1_voice_id,
                person2_voice_id,
                audio_dir,
                person1,
                person2
            )

            final_audio = combine_audio_files(audio_files, audio_dir)
            audio_path = os.path.relpath(final_audio, app.static_folder)

            return render_template('result.html',
                                   results=results,
                                   analysis=chatgpt_analysis,
                                   audio_path=audio_path)

    return render_template(UPLOAD_HTML)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
