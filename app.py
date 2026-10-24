"""Minimal upload-validation demo; use api.py for model inference."""

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    audio = request.files.get("audio")
    if audio is None or not audio.filename:
        return render_template("index.html", res="Choose an audio file to upload."), 400
    if not (audio.mimetype or "").lower().startswith("audio/"):
        return render_template("index.html", res="Upload an audio file."), 400
    return render_template("index.html", res="Audio upload accepted; this demo does not run inference.")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
