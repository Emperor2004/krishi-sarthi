"""Utility functions for Krishi Saarthi agents.

This module centralises access to JSON data and lightweight
domain configuration so that application logic does not
rely on hardcoded constants.
"""
import math
import json
import os
import tempfile
import threading
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')

_FILE_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_LOCK = threading.Lock()


def _get_file_lock(path: str) -> threading.Lock:
    with _LOCKS_LOCK:
        lock = _FILE_LOCKS.get(path)
        if lock is None:
            lock = threading.Lock()
            _FILE_LOCKS[path] = lock
        return lock


def load_json(filename: str) -> list:
    """Load a JSON array from the data directory.

    Returns an empty list when the file does not exist.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []

    lock = _get_file_lock(path)
    with lock:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filename}: {e}")
            return []


def save_json(filename: str, data) -> None:
    """Save data to a JSON file in the data directory."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    dirpath = os.path.dirname(path)
    lock = _get_file_lock(path)
    with lock:
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=dirpath, delete=False) as tmp:
                json.dump(data, tmp, indent=2, ensure_ascii=False)
                tmp.flush()
                os.fsync(tmp.fileno())
                temp_path = tmp.name
            os.replace(temp_path, path)
        except (IOError, OSError) as e:
            print(f"Error saving {filename}: {e}")
            # Attempt to create backup if original exists
            if os.path.exists(path):
                backup_path = f"{path}.backup"
                try:
                    import shutil
                    shutil.copy2(path, backup_path)
                    print(f"Created backup: {backup_path}")
                except Exception:
                    pass
            raise


@lru_cache(maxsize=1)
def load_domain_config() -> dict:
    """Load domain configuration from config/domain_config.json.

    This provides known products, unit patterns, freshness
    keywords and SMS command mappings without hardcoding
    them in Python code. If the config file is missing or
    incomplete, sensible defaults are returned.
    """
    path = os.path.join(CONFIG_DIR, 'domain_config.json')
    if not os.path.exists(path):
        return {
            "known_products": [],
            "unit_patterns": [],
            "freshness_keywords": {},
            "sms_commands": {},
        }
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        "known_products": data.get("known_products", []),
        "unit_patterns": data.get("unit_patterns", []),
        "freshness_keywords": data.get("freshness_keywords", {}),
        "sms_commands": data.get("sms_commands", {}),
    }


def euclidean_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate Euclidean distance between two lat/lng points.
    Returns approximate distance in km (mock, not geodesic).
    """
    return math.sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) * 111  # 1 degree ≈ 111km


def normalize_freshness(freshness: int) -> str:
    """Convert numeric freshness (1-5) to human-readable string."""
    labels = {
        1: "Bahut purana",
        2: "Purana",
        3: "Theek-thaak",
        4: "Taaza",
        5: "Bahut taaza",
    }
    return labels.get(freshness, "Pata nahi")


def get_vendor_by_id(vendor_id: int) -> dict:
    """Fetch a vendor record by ID."""
    from .session_agent import get_vendor_by_id as get_vendor
    return get_vendor(vendor_id)


def get_consumer_by_id(consumer_id: int) -> dict:
    """Fetch a consumer record by ID."""
    from .session_agent import get_consumer_by_id as get_consumer
    return get_consumer(consumer_id)