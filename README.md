# Synthetic Speech Detection

A Flask application for uploading an audio file and classifying it with a pretrained Hugging Face audio-classification model.

## Inference flow

1. Accept an audio upload through `POST /upload-audio` (up to 16 MB).
2. Load and resample the audio to 16 kHz with librosa.
3. Use the model’s feature extractor to prepare a five-second input window.
4. Run inference with PyTorch and display the predicted class label.

The inference implementation in `api.py` loads `idolstranger/deepfake_audio_detection`. This repository does not include a training pipeline or a reported evaluation metric, so no accuracy claim is made here. `app.py` is a simpler upload-validation app and does not run model inference.

## Stack

Python · Flask · Hugging Face Transformers · PyTorch · librosa

## Run locally

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python api.py
```

Open `http://127.0.0.1:5000`. Use only audio you have permission to process. Uploaded files are removed by the application after prediction; configure production storage, access controls, and retention deliberately before deployment.

## Repository note

The repository currently includes a `.venv` directory in Git. A virtual environment should normally be excluded with `.gitignore` and recreated from `requirements.txt`.

