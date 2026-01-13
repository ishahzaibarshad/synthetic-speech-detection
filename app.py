from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle audio file upload
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    audio = request.files.get('audio')  # Get the audio file from the form

    if audio and audio.filename != '':
        # Check if the uploaded file is an audio file by ensuring it has an audio MIME type
        audio_mime_type = audio.mimetype
        if audio_mime_type.startswith("audio/"):
            response = "Audio File Accepted Successfully!"
        else:
            response = "Uploaded file is not a valid audio format!"
        
        return render_template('index.html', res=response)
    else:
        response = "Audio File Not Found!"
        return render_template('index.html', res=response)



if __name__ == '__main__':
    app.run(debug=True)
