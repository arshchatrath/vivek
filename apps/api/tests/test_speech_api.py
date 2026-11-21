import io
import sys
import wave
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import main


client = TestClient(main.app)


def recording(rate: int = 16_000) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as clip:
        clip.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        clip.writeframes(b"\0\0" * (rate // 2))
    return buffer.getvalue()


def submit(clip: bytes, consent: bool = True):
    return client.post(
        "/api/v1/speech/transcribe",
        data={"consent": str(consent).lower()},
        files={"audio": ("concern.wav", clip, "audio/wav")},
    )


def test_voice_requires_consent():
    assert submit(recording(), consent=False).status_code == 400


def test_voice_rejects_invalid_wav(monkeypatch):
    monkeypatch.setenv("GNANI_API_KEY", "test-key")
    assert submit(recording(8_000)).status_code == 415
    assert submit(b"invalid WAV").status_code == 415


def test_voice_requires_available_quota(monkeypatch):
    monkeypatch.setenv("GNANI_API_KEY", "test-key")
    monkeypatch.setattr(main, "provider_call_allowed", lambda provider: False)
    assert submit(recording()).status_code == 429


def test_voice_returns_transcript_without_provider_metadata(monkeypatch):
    monkeypatch.setenv("GNANI_API_KEY", "test-key")
    monkeypatch.setattr(main, "provider_call_allowed", lambda provider: provider == "gnani")

    async def transcribe(self, url, *, headers, data, files):
        assert url == "https://api.vachana.ai/stt/v3"
        assert headers == {"X-API-Key-ID": "test-key"}
        assert data == {"language_code": "en-IN"}
        assert files["audio_file"][2] == "audio/wav"
        return httpx.Response(200, request=httpx.Request("POST", url), json={
            "success": True,
            "transcript": "  My scalp is itchy.  ",
            "request_id": "provider-only",
        })

    monkeypatch.setattr(main.httpx.AsyncClient, "post", transcribe)
    response = submit(recording())
    assert response.status_code == 200
    assert response.json() == {"transcript": "My scalp is itchy.", "provider": "gnani"}
