import io
import tempfile

import pytest

import api


@pytest.fixture
def client():
    api.app.config.update(TESTING=True)
    return api.app.test_client()


def test_homepage_renders(client):
    response = client.get("/")
    assert response.status_code == 200


def test_upload_runs_classifier_and_removes_temporary_audio(client, monkeypatch, tmp_path):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(api, "predict_audio_class", lambda _path: "synthetic")

    response = client.post(
        "/upload-audio",
        data={"audio": (io.BytesIO(b"audio bytes"), "sample.wav", "audio/wav")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Prediction: synthetic" in response.data
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [("", "audio/wav"), ("sample.txt", "text/plain")],
)
def test_upload_rejects_empty_or_unsupported_file(client, filename, content_type):
    response = client.post(
        "/upload-audio",
        data={"audio": (io.BytesIO(b"data"), filename, content_type)},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_decode_error_is_reported_without_internal_details(client, monkeypatch):
    def reject_audio(_path):
        raise api.InvalidAudioError("private filesystem detail")

    monkeypatch.setattr(api, "predict_audio_class", reject_audio)
    response = client.post(
        "/upload-audio",
        data={"audio": (io.BytesIO(b"not audio"), "sample.wav", "audio/wav")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 422
    assert b"private filesystem detail" not in response.data


def test_inference_error_returns_service_unavailable(client, monkeypatch):
    def fail_inference(_path):
        raise RuntimeError("internal error detail")

    monkeypatch.setattr(api, "predict_audio_class", fail_inference)
    response = client.post(
        "/upload-audio",
        data={"audio": (io.BytesIO(b"audio"), "sample.wav", "audio/wav")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 503
    assert b"internal error detail" not in response.data


def test_upload_size_limit_returns_413(client):
    api.app.config["MAX_CONTENT_LENGTH"] = 4
    response = client.post(
        "/upload-audio",
        data={"audio": (io.BytesIO(b"12345"), "sample.wav", "audio/wav")},
        content_type="multipart/form-data",
    )
    api.app.config["MAX_CONTENT_LENGTH"] = api.MAX_UPLOAD_BYTES
    assert response.status_code == 413
