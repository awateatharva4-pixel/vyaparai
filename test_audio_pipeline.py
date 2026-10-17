import sys
import os
import io
import wave
import struct

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(__file__))

from starlette.testclient import TestClient
from app.main import app
from app.services.gemini_service import GeminiService
from app.services.audio_service import AudioNormalizer

def generate_sample_wav() -> bytes:
    """Generates a valid 0.5-second PCM WAV file in memory."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # 0.5 seconds of low frequency tone
        frames = bytearray()
        for i in range(8000):
            val = int(3000 * ((i % 16) / 8.0 - 1.0))
            frames.extend(struct.pack('<h', val))
        wav_file.writeframes(frames)
    return buf.getvalue()

def test_audio_pipeline():
    client = TestClient(app)
    sample_wav = generate_sample_wav()
    print(f"Generated sample WAV: {len(sample_wav)} bytes")

    # 1. Test AudioNormalizer with FFmpeg
    print("\n--- 1. Testing AudioNormalizer ---")
    norm_bytes, mime = AudioNormalizer.normalize_audio(sample_wav, input_format="wav")
    assert len(norm_bytes) > 0
    assert mime in ("audio/wav", "audio/ogg")
    print(f"AudioNormalizer OK! Output: {len(norm_bytes)} bytes, MIME: {mime}")

    # 2. Test GeminiService.transcribe_and_parse_audio
    print("\n--- 2. Testing GeminiService.transcribe_and_parse_audio ---")
    catalog = [
        {"sku": "GRO-SUG-001", "name_mr": "साखर", "name_en": "Sugar", "aliases": ["sakhar", "sugar"]}
    ]
    empty_res = GeminiService.transcribe_and_parse_audio(b"")
    assert empty_res["source"] == "empty-audio"
    print("Empty audio handling verified!")

    audio_res = GeminiService.transcribe_and_parse_audio(sample_wav, mime_type="audio/wav", catalog=catalog)
    assert "transcription" in audio_res
    assert "intent" in audio_res
    print(f"transcribe_and_parse_audio OK! Intent: {audio_res.get('intent')}, Source: {audio_res.get('source')}")

    # 3. Test POST /api/simulator/audio
    print("\n--- 3. Testing POST /api/simulator/audio ---")
    r3 = client.post(
        "/api/simulator/audio",
        files={"file": ("kirana_voice.wav", sample_wav, "audio/wav")},
        data={"vendor_id": "DEMO_KIRANA_KOP"}
    )
    assert r3.status_code == 200
    data3 = r3.json()
    assert "reply" in data3
    assert "transcription" in data3
    assert "🎙️ *ऑडिओ ऐकले:*" in data3["reply"]
    print(f"Simulator Audio API OK! Reply preview: {data3['reply'].splitlines()[0]}")

    # 4. Test Green-API Audio Webhook Ingress
    print("\n--- 4. Testing POST /api/v1/webhook/whatsapp (Green-API voiceMessage) ---")
    green_audio_payload = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {"idInstance": 710722771292, "wid": "917558455021@c.us"},
        "idMessage": "MSG_AUDIO_TEST_001",
        "senderData": {"chatId": "917558455021@c.us", "sender": "917558455021@c.us"},
        "messageData": {
            "typeMessage": "voiceMessage",
            "fileMessageData": {
                "downloadUrl": "",
                "mimeType": "audio/ogg",
                "caption": ""
            }
        }
    }
    r4 = client.post("/api/v1/webhook/whatsapp", json=green_audio_payload)
    assert r4.status_code == 200
    assert r4.text == "EVENT_RECEIVED"
    print("Green-API Audio Ingress OK! (Status 200 EVENT_RECEIVED)")

    # 5. Test Meta Cloud API Audio Webhook Ingress
    print("\n--- 5. Testing POST /api/v1/webhook/whatsapp (Meta Cloud API Audio) ---")
    meta_audio_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "12345", "phone_number_id": "67890"},
                    "messages": [{
                        "from": "919579869506",
                        "id": "WAMID_TEST_AUDIO_002",
                        "timestamp": "1729000000",
                        "type": "audio",
                        "audio": {"id": "MEDIA_ID_12345", "mime_type": "audio/ogg"}
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    r5 = client.post("/api/v1/webhook/whatsapp", json=meta_audio_payload)
    assert r5.status_code == 200
    assert r5.text == "EVENT_RECEIVED"
    print("Meta Audio Ingress OK! (Status 200 EVENT_RECEIVED)")

    # 6. Test GET /test-console contains Voice and Microphone controls
    print("\n--- 6. Testing GET /test-console (UI Verification) ---")
    r6 = client.get("/test-console")
    assert r6.status_code == 200
    assert "micBtn" in r6.text
    assert "recordingStatus" in r6.text
    assert "audioFileInput" in r6.text
    assert "SpeechRecognition" in r6.text
    assert "mr-IN" in r6.text
    assert "MediaRecorder" in r6.text
    assert "/api/simulator/audio" in r6.text
    print("Simulator UI contains all Audio & Web Speech features! (Status 200)")

    print("\n=======================================================")
    print(">>> ALL AUDIO & WEBHOOK PATCHES VERIFIED 100% OPERATIONAL! <<<")
    print("=======================================================")

if __name__ == "__main__":
    test_audio_pipeline()
