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

    _cached_ffmpeg_bin: Optional[str] = None

    @classmethod
    def get_ffmpeg_binary(cls) -> Optional[str]:
        """Resolves FFmpeg binary path with caching: imageio_ffmpeg -> system PATH."""
        if cls._cached_ffmpeg_bin and os.path.exists(cls._cached_ffmpeg_bin):
            return cls._cached_ffmpeg_bin

        # 1. Bundled imageio-ffmpeg (offline wheel static binary)
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                cls._cached_ffmpeg_bin = exe
                return exe
        except Exception:
            pass

        # 2. System PATH
        import shutil
        sys_exe = shutil.which("ffmpeg")
        if sys_exe:
            cls._cached_ffmpeg_bin = sys_exe
            return sys_exe

        return "ffmpeg"

    @classmethod
    def normalize_audio(cls, audio_bytes: bytes, input_format: Optional[str] = "ogg") -> Tuple[bytes, str]:
        """
        Attempts FFmpeg-based bandpass filtering (300Hz-3400Hz vocal band)
        and normalizes output to 16kHz mono 16-bit PCM WAV for Google STT / Gemini.
        Guarantees zero unhandled exceptions on silence, corrupted bytes, or conversion timeouts.
        """
        if not audio_bytes:
            return b"", "audio/ogg"

        clean_format = (input_format or "ogg").split(";")[0].replace("audio/", "").replace(".", "").strip().lower()
        if clean_format in ("opus", ""):
            clean_format = "ogg"
        elif clean_format in ("wave", "x-wav"):
            clean_format = "wav"
        elif clean_format in ("mpeg",):
            clean_format = "mp3"

        mime_map = {
            "ogg": "audio/ogg",
            "opus": "audio/ogg",
            "wav": "audio/wav",
            "wave": "audio/wav",
            "x-wav": "audio/wav",
            "mp3": "audio/mp3",
            "mpeg": "audio/mp3",
            "webm": "audio/webm",
            "m4a": "audio/m4a",
            "mp4": "audio/mp4",
            "aac": "audio/aac",
            "amr": "audio/amr",
            "flac": "audio/flac"
        }
        fallback_mime = mime_map.get(clean_format, "audio/ogg")

        ffmpeg_bin = cls.get_ffmpeg_binary() or "ffmpeg"

        try:
            cmd = [
                ffmpeg_bin,
                "-y",
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
            if process.returncode == 0 and len(out) > 100:
                print(f"[AUDIO NORMALIZER]: Normalized {len(audio_bytes)}B audio to {len(out)}B WAV via FFmpeg ({ffmpeg_bin})")
                return out, "audio/wav"
            else:
                print(f"[AUDIO NORMALIZER WARN]: FFmpeg conversion exited with code {process.returncode}, output len {len(out)}")
        except subprocess.TimeoutExpired:
            try:
                process.kill()
                process.communicate()
            except Exception:
                pass
            print(f"[AUDIO NORMALIZER WARN]: FFmpeg conversion timed out after 10s")
        except Exception as e:
            print(f"[AUDIO NORMALIZER WARN]: FFmpeg conversion failed: {e}")

        # Return original audio with sanitized IANA MIME type for Gemini
        return audio_bytes, fallback_mime
