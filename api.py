from functools import lru_cache
import logging
import os
from pathlib import Path
import tempfile

from flask import Flask, current_app, render_template, request
from werkzeug.datastructures import FileStorage

MODEL_ID = "idolstranger/deepfake_audio_detection"
MAX_UPLOAD_BYTES = 16 * 1024 * 1024
MAX_AUDIO_SECONDS = 60
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


class InvalidAudioError(ValueError):
    """Raised when an uploaded file cannot be decoded as supported audio."""


@lru_cache(maxsize=1)
def load_model():
    """Load the public Hugging Face model only when the first prediction is requested."""
    import torch
    from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

    model = AutoModelForAudioClassification.from_pretrained(MODEL_ID)
    model.eval()
    extractor = AutoFeatureExtractor.from_pretrained(MODEL_ID)
    return model, extractor, torch


def predict_audio_class(audio_path: str) -> str:
    """Run CPU inference on at most five seconds from a bounded audio decode."""
    import librosa

    model, extractor, torch = load_model()
    try:
        speech, _ = librosa.load(audio_path, sr=16_000, duration=MAX_AUDIO_SECONDS)
    except Exception as exc:
        raise InvalidAudioError("The uploaded file could not be decoded.") from exc
    if speech.size == 0:
        raise InvalidAudioError("The uploaded audio is empty.")

    inputs = extractor(
        speech,
        sampling_rate=16_000,
        return_tensors="pt",
        padding="max_length",
        max_length=16_000 * 5,
        truncation=True,
    )
    with torch.inference_mode():
        logits = model(**inputs).logits

    class_id = int(logits.argmax(dim=-1).item())
    labels = model.config.id2label
    return str(labels.get(class_id, class_id))


def _render(message: str, status: int):
    return render_template("index.html", res=message), status


@app.errorhandler(413)
def upload_too_large(_error):
    return _render("Audio file exceeds the 16 MB upload limit.", 413)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    audio: FileStorage | None = request.files.get("audio")
    if audio is None or not audio.filename:
        return _render("Choose an audio file to upload.", 400)

    suffix = Path(audio.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS or not (audio.mimetype or "").lower().startswith("audio/"):
        return _render("Upload a supported audio file.", 400)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="speech-detection-", suffix=suffix, delete=False) as temp_file:
            temp_path = temp_file.name
        audio.save(temp_path)
        try:
            prediction = predict_audio_class(temp_path)
        except InvalidAudioError:
            return _render("The uploaded audio could not be decoded. Try a valid audio file.", 422)
        except Exception:
            current_app.logger.exception("Audio inference failed")
            return _render("The classifier is unavailable. Check the local model setup and try again.", 503)
        return _render(f"Prediction: {prediction}", 200)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
