"""Utility modules for Krishi Saarthi."""

from .speech_utils import (
    transcribe_audio_to_text,
    synthesize_text_to_speech_hi,
    encode_audio_base64,
    has_stt_backend,
    has_tts_backend,
)
from .utils import (
    load_json,
    save_json,
    load_domain_config,
    euclidean_distance,
    normalize_freshness,
    get_vendor_by_id,
    get_consumer_by_id,
)

__all__ = [
    "transcribe_audio_to_text",
    "synthesize_text_to_speech_hi",
    "encode_audio_base64",
    "has_stt_backend",
    "has_tts_backend",
    "load_json",
    "save_json",
    "load_domain_config",
    "euclidean_distance",
    "normalize_freshness",
    "get_vendor_by_id",
    "get_consumer_by_id",
]