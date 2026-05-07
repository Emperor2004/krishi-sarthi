"""
Krishi Saarthi – FastAPI Backend
Multi-agent AI system for rural agricultural commerce.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
import uvicorn
import json

from src.krishi.utils.speech_utils import (
    transcribe_audio_to_text,
    synthesize_text_to_speech_hi,
    encode_audio_base64,
    has_stt_backend,
    has_tts_backend,
)

from src.krishi.services.session_agent import (
    register_user,
    login_user,
    validate_session,
    logout_user,
    update_user_profile,
    cleanup_expired_sessions,
)

from src.krishi.services.listing_agent import extract_product
from src.krishi.services.discovery_agent import search_products
from src.krishi.services.udhar_agent import create_udhar, pay_udhar, get_audit_log
from src.krishi.services.fallback_agent import parse_sms, get_ussd_tree
from src.krishi.utils.utils import load_json, save_json
from src.krishi.core.conversation_agent import handle_conversation

# ──────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("krishi_saarthi")

app = FastAPI(
    title="Krishi Saarthi API",
    description="Voice-first multi-agent AI system for rural agricultural commerce",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Serve frontend (web app) from /app
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


# ──────────────────────────────────────────────
# Request Models
# ──────────────────────────────────────────────
class ListingRequest(BaseModel):
    voice_text: str
    vendor_id: int


class DiscoveryRequest(BaseModel):
    query_text: str
    consumer_id: int


class UdharCreateRequest(BaseModel):
    vendor_id: int
    consumer_name: str
    amount: float


class UdharPayRequest(BaseModel):
    transaction_id: str
    amount_paid: Optional[float] = None


class SMSRequest(BaseModel):
    message: str


class VoiceRequest(BaseModel):
    session_token: str  # Changed from user_id to session_token
    voice_text: str
    language: Optional[str] = "hi"
    state: Optional[Dict[str, Any]] = None


class VoiceAudioResponse(BaseModel):
    """Response model for audio+text voice conversations.

    This is useful for clients that want both the Hindi text reply
    (for display) and ready-to-play audio (base64 encoded MP3).
    """

    reply_text: str
    user_text: Optional[str] = None
    action: Optional[str]
    data: Dict[str, Any]
    next_state: Dict[str, Any]
    audio_base64: Optional[str] = None


class RegisterRequest(BaseModel):
    phone: str
    name: str
    role: str  # "vendor" or "consumer"
    password: str
    address: Optional[str] = None


class LoginRequest(BaseModel):
    phone: str
    password: str


class ProfileUpdateRequest(BaseModel):
    session_token: str
    updates: Dict[str, Any]


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "online", "project": "Krishi Saarthi", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "stt_available": has_stt_backend(),
        "tts_available": has_tts_backend(),
        "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "phi3:latest"),
    }


@app.post("/api/voice")
def voice_endpoint(req: VoiceRequest):
    """Single conversational endpoint for all voice-first flows.

    This behaves like a human assistant: it detects intent, manages
    multi-step state, and always returns Hindi reply_text suitable
    for text-to-speech.
    """
    # Validate session
    session_data = validate_session(req.session_token)
    if not session_data:
        return {
            "reply_text": "Session expired. Please login again.",
            "action": "session_expired",
            "data": {},
            "next_state": {},
        }

    user_id = session_data["user_id"]
    role = session_data["role"]

    result = handle_conversation(
        user_id=user_id,
        role=role,
        voice_text=req.voice_text,
        state=req.state or {},
    )
    # Ensure minimal contract is always present
    if "reply_text" not in result:
        result["reply_text"] = "Mujhe samajh nahi aaya, kripya dobara boliye."
    result.setdefault("action", None)
    result.setdefault("data", {})
    result.setdefault("next_state", {})
    return result


@app.post("/api/voice-audio", response_model=VoiceAudioResponse)
async def voice_audio_endpoint(
    session_token: str = Form(...),
    state: str = Form("{}"),  # JSON-encoded state from previous turn
    language: str = Form("hi"),
    audio_file: UploadFile = File(...),
):
    """Voice + text endpoint.

    - Client sends recorded audio plus session_token, and previous state.
    - Server converts audio to Hindi text, runs the conversation agent,
      and returns both reply_text and (optionally) TTS audio.
    """
    # Validate session
    session_data = validate_session(session_token)
    if not session_data:
        return VoiceAudioResponse(
            reply_text="Session expired. Please login again.",
            user_text=None,
            action="session_expired",
            data={},
            next_state={},
            audio_base64=None,
        )

    user_id = session_data["user_id"]
    role = session_data["role"]

    # Read audio bytes
    audio_bytes = await audio_file.read()

    # Step 1: STT – convert voice to text (Hindi)
    voice_text = transcribe_audio_to_text(audio_bytes, language=language or "hi")
    if not voice_text:
        # If STT is not configured or failed, guide user in Hindi
        return VoiceAudioResponse(
            reply_text="Awaz samajh nahi aayi ya STT band hai. Kripya text se message bhejiye.",
            user_text=None,
            action="stt_unavailable",
            data={},
            next_state={},
            audio_base64=None,
        )

    # Parse JSON state safely
    try:
        state_obj: Dict[str, Any] = json.loads(state or "{}")
    except Exception:
        state_obj = {}

    # Step 2: run main conversation engine (same as /api/voice)
    conv_result = handle_conversation(
        user_id=user_id,
        role=role,
        voice_text=voice_text,
        state=state_obj,
    )

    if "reply_text" not in conv_result:
        conv_result["reply_text"] = "Mujhe samajh nahi aaya, kripya dobara boliye."
    conv_result.setdefault("action", None)
    conv_result.setdefault("data", {})
    conv_result.setdefault("next_state", {})

    # Step 3: TTS – create Hindi audio for reply (if possible)
    tts_bytes = synthesize_text_to_speech_hi(conv_result["reply_text"])
    audio_b64 = encode_audio_base64(tts_bytes) if tts_bytes else None

    return VoiceAudioResponse(
        reply_text=conv_result["reply_text"],
        user_text=voice_text,
        action=conv_result.get("action"),
        data=conv_result.get("data", {}),
        next_state=conv_result.get("next_state", {}),
        audio_base64=audio_b64,
    )


@app.get("/api/vendors")
def get_vendors():
    """Return list of all vendors."""
    return load_json('vendors.json')


@app.get("/api/consumers")
def get_consumers():
    """Return list of all consumers."""
    return load_json('consumers.json')


@app.post("/api/listing")
def listing_endpoint(req: ListingRequest):
    """
    Listing Agent: Convert vendor voice/text into structured product listing.
    Saves the product to inventory.
    """
    if not req.voice_text.strip():
        raise HTTPException(status_code=400, detail="voice_text khaali nahi ho sakta, kripya apni baat boliye.")

    product = extract_product(req.voice_text)

    # Save to inventory
    inventory = load_json('inventory.json')
    from datetime import datetime
    new_item = {
        "id": max((i['id'] for i in inventory), default=0) + 1,
        "vendor_id": req.vendor_id,
        "product_name": product.get("product", "Unknown"),
        "price": product.get("price", 0),
        "unit": product.get("unit", "kg"),
        "quantity": product.get("quantity", 0),
        "freshness": product.get("freshness", 3),
        "timestamp": datetime.now().isoformat(timespec='seconds')
    }
    inventory.append(new_item)
    save_json('inventory.json', inventory)

    return {
        "success": True,
        "extracted": product,
        "saved_item": new_item,
        "message": f"Samaan '{new_item['product_name']}' safalta se jod diya gaya hai."
    }


@app.post("/api/discovery")
def discovery_endpoint(req: DiscoveryRequest):
    """
    Discovery Agent: Search and rank products based on consumer voice query.
    """
    if not req.query_text.strip():
        raise HTTPException(status_code=400, detail="query_text khaali nahi ho sakta, kripya apni baat boliye.")

    result = search_products(req.query_text, req.consumer_id)
    return result


@app.post("/api/udhar/create")
def udhar_create_endpoint(req: UdharCreateRequest):
    """
    Udhar Agent: Create a new credit entry with immutable audit trail.
    """
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Rakam zero se zyada honi chahiye.")
    if not req.consumer_name.strip():
        raise HTTPException(status_code=400, detail="Graahak ka naam khaali nahi ho sakta, kripya naam batayein.")

    result = create_udhar(req.vendor_id, req.consumer_name.strip(), req.amount)
    return result


@app.post("/api/udhar/pay")
def udhar_pay_endpoint(req: UdharPayRequest):
    """
    Udhar Agent: Record payment against an udhar transaction.
    """
    if not req.transaction_id.strip():
        raise HTTPException(status_code=400, detail="transaction_id khaali nahi ho sakta, kripya ID batayein.")

    result = pay_udhar(req.transaction_id.strip().upper(), req.amount_paid)
    if not result['success']:
        raise HTTPException(status_code=404, detail=result['message'])
    return result


@app.get("/api/udhar/audit/{vendor_id}")
def udhar_audit_endpoint(vendor_id: int):
    """
    Udhar Agent: Fetch full audit log for a vendor's udhar transactions.
    """
    return get_audit_log(vendor_id)


@app.post("/api/fallback/sms")
def sms_endpoint(req: SMSRequest):
    """
    Fallback Agent: Parse SMS command and return plain-text response.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Sandesh khaali nahi ho sakta, kripya apna message likhiye.")

    response = parse_sms(req.message)
    return {"input": req.message, "response": response}


@app.get("/api/fallback/ussd")
def ussd_endpoint():
    """
    Fallback Agent: Return static USSD menu tree.
    """
    return get_ussd_tree()


# ──────────────────────────────────────────────
# Authentication Routes
# ──────────────────────────────────────────────

@app.post("/api/auth/register")
def register_endpoint(req: RegisterRequest):
    """Register a new user (vendor or consumer)."""
    result = register_user(
        phone=req.phone,
        name=req.name,
        role=req.role,
        password=req.password,
        address=req.address,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@app.post("/api/auth/login")
def login_endpoint(req: LoginRequest):
    """Authenticate user and return session token."""
    result = login_user(req.phone, req.password)

    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])

    return result


@app.post("/api/auth/logout")
def logout_endpoint(session_token: str):
    """Invalidate user session (logout)."""
    success = logout_user(session_token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid session token.")

    return {"message": "Logout successful."}


@app.post("/api/auth/profile")
def profile_update_endpoint(req: ProfileUpdateRequest):
    """Update user profile information."""
    session_data = validate_session(req.session_token)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    success = update_user_profile(session_data["user_id"], req.updates)
    if not success:
        raise HTTPException(status_code=400, detail="Profile update failed.")

    return {"message": "Profile updated successfully."}


@app.get("/api/auth/validate")
def validate_session_endpoint(session_token: str):
    """Validate session token and return user info."""
    session_data = validate_session(session_token)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    return session_data


@app.post("/api/auth/cleanup")
def cleanup_sessions_endpoint():
    """Clean up expired sessions (admin/maintenance endpoint)."""
    cleaned_count = cleanup_expired_sessions()
    return {"message": f"Cleaned up {cleaned_count} expired sessions."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)