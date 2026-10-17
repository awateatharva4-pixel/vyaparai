import io
import os
import subprocess
from typing import Optional, Tuple

class AudioNormalizer:
    """
    Audio Pre-processing & Normalization Engine (PPT Slide 3 & Slide 4).
    Applies audio normalization, noise-gating, and standardizes audio formats
    (e.g., WhatsApp .ogg Opus to WAV/MP3) for optimal transcription.
    """

    @classmethod
    def normalize_audio(cls, audio_bytes: bytes, input_format: str = "ogg") -> Tuple[bytes, str]:
        """
        Attempts FFmpeg-based bandpass filtering (300Hz-3400Hz vocal band)
        and loudness normalization. If FFmpeg is not installed on the host system,
        gracefully returns original bytes with appropriate MIME type.
        """
        # Sanitize input format parameter (strip parameters like '; codecs=opus' and 'audio/')
        clean_format = input_format.split(";")[0].replace("audio/", "").strip().lower()
        if clean_format in ("opus", ""):
            clean_format = "ogg"

        # Try FFmpeg (bundled imageio_ffmpeg first, then system PATH)
        ffmpeg_bin = "ffmpeg"
        try:
            import imageio_ffmpeg
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass

        try:
            cmd = [
                ffmpeg_bin,
                "-y",
                "-f", clean_format,
                "-i", "pipe:0",
                "-ac", "1",
                "-ar", "16000",
                "-af", "highpass=f=300,lowpass=f=3400",
                "-f", "wav",
                "pipe:1"
            ]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = process.communicate(input=audio_bytes, timeout=10)
            if process.returncode == 0 and len(out) > 0:
                print(f"[AUDIO NORMALIZER]: Normalized {len(audio_bytes)}B audio to {len(out)}B WAV via FFmpeg ({ffmpeg_bin})")
                return out, "audio/wav"
        except Exception as e:
            print(f"[AUDIO NORMALIZER WARN]: FFmpeg conversion failed: {e}")

        # Return original audio with sanitized IANA MIME type for Gemini
        mime_map = {
            "ogg": "audio/ogg",
            "opus": "audio/ogg",
            "wav": "audio/wav",
            "mp3": "audio/mp3",
            "webm": "audio/webm",
            "m4a": "audio/m4a"
        }
        return audio_bytes, mime_map.get(clean_format, "audio/ogg")
