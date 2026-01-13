from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch
import librosa
import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Load model and feature extractor
model = AutoModelForAudioClassification.from_pretrained("idolstranger/deepfake_audio_detection")
feature_extractor = AutoFeatureExtractor.from_pretrained("idolstranger/deepfake_audio_detection")

def predict_audio_class(audio_path):
    # Load audio
    speech, sr = librosa.load(audio_path, sr=16000)

    # Preprocess
    inputs = feature_extractor(
        speech,
        sampling_rate=sr,
        return_tensors="pt",
        padding="max_length",
        max_length=16000 * 5,  # 5 seconds
        truncation=True
    )

    # Inference
    with torch.no_grad():
        logits = model(**inputs).logits

    # Get prediction
    id2label = model.config.id2label
    predicted_class = logits.argmax().item()
    return id2label[predicted_class]

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle audio file upload and prediction
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return render_template('index.html', res="No audio file uploaded")
    
    audio = request.files['audio']
    
    if audio.filename == '':
        return render_template('index.html', res="No selected file")
    
    if audio and audio.mimetype.startswith("audio/"):
        filename = secure_filename(audio.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio.save(save_path)
        
        try:
            prediction = predict_audio_class(save_path)
            result = f"Prediction: {prediction}"
        except Exception as e:
            result = f"Error processing audio: {str(e)}"
        finally:
            if os.path.exists(save_path):
                os.remove(save_path)
        
        return render_template('index.html', res=result)
    else:
        return render_template('index.html', res="Invalid file format - audio files only")

if __name__ == '__main__':
    app.run(debug=True)