"""Speech utilities for Krishi Saarthi.

This module provides helper functions to:
- convert audio bytes (voice input) to Hindi text using a local STT engine
- convert Hindi text replies to audio bytes using a TTS engine

By default, these functions try to use optional third‑party libraries.
You can swap implementations depending on your deployment.
"""
from __future__ import annotations

import base64
import logging
import os
import shutil
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)

# STT: Whisper (local, offline). Install with:
#   pip install git+https://github.com/openai/whisper.git
try:  # pragma: no cover - optional dependency
    import whisper  # type: ignore
    _whisper_model: Optional["whisper.Whisper"] = None
except Exception:  # pragma: no cover - optional dependency missing
    whisper = None  # type: ignore
    _whisper_model = None
    logger.warning("Whisper is not installed; speech-to-text will be unavailable.")

# Optional helper binary provider for ffmpeg when the system does not have it.
# Install with: pip install imageio-ffmpeg
try:  # pragma: no cover - optional dependency
    from imageio_ffmpeg import get_ffmpeg_exe  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    get_ffmpeg_exe = None  # type: ignore

# TTS: gTTS (simple Hindi TTS, needs internet). Install with:
#   pip install gTTS
try:  # pragma: no cover - optional dependency
    from gtts import gTTS  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    gTTS = None  # type: ignore
    logger.warning("gTTS is not installed; text-to-speech audio will be unavailable.")


def _ensure_ffmpeg_available() -> bool:
    """Ensure ffmpeg is available for Whisper audio decoding."""
    if shutil.which("ffmpeg"):
        return True

    if get_ffmpeg_exe is None:
        logger.warning("ffmpeg is not installed and imageio-ffmpeg is unavailable.")
        return False

    try:
        ffmpeg_path = get_ffmpeg_exe()
        if ffmpeg_path and os.path.isfile(ffmpeg_path):
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            os.environ["PATH"] = os.pathsep.join([ffmpeg_dir, os.environ.get("PATH", "")])
            os.environ["FFMPEG_BINARY"] = ffmpeg_path
            logger.info("Configured bundled ffmpeg executable: %s", ffmpeg_path)
            return True
    except Exception as exc:
        logger.warning("Failed to configure bundled ffmpeg: %s", exc)

    logger.warning("ffmpeg binary unavailable for Whisper audio decoding.")
    return False


def transcribe_audio_to_text(audio_bytes: bytes, language: str = "hi") -> str:
    """Convert raw audio bytes to text using Whisper if available.

    Parameters
    ----------
    audio_bytes: bytes
        Binary audio data (e.g. WAV/MP3/OGG) from UploadFile.
    language: str
        Target language hint (default "hi" for Hindi).

    Returns
    -------
    str
        Transcribed text. If no STT engine is available, returns empty string.
    """
    if whisper is None:
        logger.warning("Whisper STT backend not installed. Returning empty transcription.")
        return ""

    if not _ensure_ffmpeg_available():
        logger.warning("Whisper STT cannot decode audio because ffmpeg is missing.")
        return ""

    global _whisper_model
    try:
        if _whisper_model is None:
            # Load a small multilingual model; adjust as needed
            _whisper_model = whisper.load_model("small")

        # Whisper expects a file-like object; wrap bytes in BytesIO
        with BytesIO(audio_bytes) as buf:
            # Let Whisper handle format detection; language is a hint
            result = _whisper_model.transcribe(buf, language=language)
        text = (result.get("text") or "").strip()
        return text
    except Exception as exc:
        logger.exception("Whisper transcription failed")
        return ""


def synthesize_text_to_speech_hi(text: str) -> bytes:
    """Convert Hindi text to speech audio bytes using gTTS if available.

    Returns raw MP3 bytes. If TTS is not available, returns empty bytes.
    The caller can decide whether to fall back to text-only when this is empty.
    """
    if not text:
        return b""
    if gTTS is None:
        logger.warning("gTTS backend not installed. Returning empty audio bytes.")
        return b""

    try:
        buf = BytesIO()
        tts = gTTS(text=text, lang="hi")
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as exc:
        logger.exception("TTS generation failed")
        return b""


def encode_audio_base64(audio_bytes: bytes) -> str:
    """Encode audio bytes to base64 string for JSON APIs."""
    if not audio_bytes:
        return ""
    return base64.b64encode(audio_bytes).decode("ascii")


def has_stt_backend() -> bool:
    """Return True when Whisper-based STT is installed and available."""
    return whisper is not None


def has_tts_backend() -> bool:
    """Return True when gTTS-based TTS is installed and available."""
    return gTTS is not None
