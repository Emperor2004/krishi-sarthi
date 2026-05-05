# 🌾 Krishi Saarthi — कृषि सारथी

**Voice-First Multi-Agent AI System for Rural Agricultural Commerce**

> Hackathon Project | Problem Statement #5 – Domain-Specialized AI Agents with Compliance Guardrails

---

## 📁 Project Structure (Reorganized)

```
krishi-sarthi/
├── main.py                    # FastAPI application entrypoint
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Python project configuration
├── .env / .env.example        # Environment configuration
├── src/                      # Source code package
│   └── krishi/
│       ├── __init__.py
│       ├── core/             # Core business logic
│       │   ├── __init__.py
│       │   └── conversation_agent.py
│       ├── services/         # Domain services
│       │   ├── __init__.py
│       │   ├── listing_agent.py
│       │   ├── discovery_agent.py
│       │   ├── udhar_agent.py
│       │   ├── fallback_agent.py
│       │   └── session_agent.py
│       └── utils/            # Shared utilities
│           ├── __init__.py
│           ├── speech_utils.py
│           └── utils.py
├── frontend/                 # React/Vue-style frontend
│   ├── package.json
│   ├── vite.config.mjs
│   ├── index.html
│   ├── public/               # Static assets
│   └── src/
│       ├── main.js           # Entry point
│       ├── components/       # UI components
│       ├── utils/            # Frontend utilities
│       │   └── script.js     # Main app logic
│       └── assets/           # Styles, images
│           └── style.css
├── data/                     # Runtime data storage
├── tests/                    # Test suite
├── scripts/                  # Development scripts
│   ├── setup.py             # Environment setup
│   └── dev.py               # Development tasks
└── docs/                    # Documentation
    └── README.md
```

---

## 🚀 Quick Start

### Automated Setup
```bash
git clone <repo-url>
cd krishi-sarthi

# Run automated setup (creates venv, installs deps)
python scripts/dev.py setup
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install
cd ..
```

### Configuration
```bash
# Copy environment template
copy .env.example .env

# Edit .env for your setup (Ollama host, etc.)
```

### Running the Application
```bash
# Backend (terminal 1)
python scripts/dev.py backend

# Frontend (terminal 2)
python scripts/dev.py frontend
```

---

## 🛠️ Development Workflow

### Available Commands
```bash
# Setup environment
python scripts/dev.py setup

# Start services
python scripts/dev.py backend   # FastAPI server
python scripts/dev.py frontend  # Vite dev server

# Testing & Quality
python scripts/dev.py test      # Run test suite
python scripts/dev.py lint      # Code linting

# Maintenance
python scripts/dev.py clean     # Clean data files
```

### Project Structure Details
- **`src/krishi/`**: Main Python package
  - `core/`: Conversation engine and business logic
  - `services/`: Domain-specific services (listing, payments, auth)
  - `utils/`: Shared utilities and helpers
- **`frontend/`**: Modern frontend with component structure
- **`tests/`**: Comprehensive test suite
- **`scripts/`**: Development and deployment automation
- **`docs/`**: Detailed documentation
# Install gTTS for Hindi TTS and Whisper for local STT if you want full voice support.
# See requirements.txt comments for the optional package names.

# Notes:
# - The backend can still start without these packages.
# - /api/voice remains available for text-only conversational access.
# - /api/voice-audio will fallback to text-only mode when STT or TTS is unavailable.
```

### 3. Start backend API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API base: http://localhost:8000  
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

### 4. Frontend setup (Vite web app)

In a **new terminal**, from the `frontend/` folder:

```bash
cd frontend
npm install
npm run dev
```

- Vite dev server: usually http://localhost:5173/  
- Proxy is configured so all `/api/*` requests go to `http://localhost:8000`.

### 5. Use the app

1. Open `http://localhost:5173/` in a modern browser (Chrome/Edge).  
2. On the landing screen, choose **Vendor (विक्रेता)** or **Consumer (ग्राहक)**.  
3. On the assistant screen, press the big mic button and speak in Hindi.  
4. The app sends audio to `/api/voice-audio`, and shows:
    - Your recognized text (`user_text`) under **"आपकी बात"**, and  
    - Krishi Saarthi’s reply (`reply_text`) under **"सारथी का जवाब"**, plus spoken audio.

---




## 🏗️ High-Level Architecture

```
Browser (Vite Web App)
 ├─ Landing screen: choose Vendor / Consumer
 └─ Voice assistant screen: mic, bubbles, Hindi text
    │
    │  /api/voice-audio  (audio + state)
    ▼
FastAPI Backend (main.py)
 ├─ /api/voice           → text in / text out
 ├─ /api/voice-audio     → audio in / text + audio out
 └─ Conversation engine  → agents.conversation_agent.handle_conversation
    │
    ├─ ListingAgent      (agents/listing_agent.py)
    ├─ DiscoveryAgent    (agents/discovery_agent.py)
    ├─ UdharAgent        (agents/udhar_agent.py)
    └─ FallbackAgent     (agents/fallback_agent.py)
    │
    └─ JSON data in /data (vendors, consumers, inventory, orders, udhar_ledger, pending_udhar)
```

---

## 🔐 Authentication & User Management

Krishi Saarthi uses session-based authentication with secure tokens. Users must register and login before accessing voice features.

### Authentication Endpoints

```bash
POST /api/auth/register
# Register new user (vendor/consumer)
{
  "phone": "9876543210",
  "name": "Rajesh Kumar",
  "role": "vendor",  # or "consumer"
  "password": "secure123",
  "address": "Village Name"  # optional
}

POST /api/auth/login
# Login and get session token
{
  "phone": "9876543210",
  "password": "secure123"
}
# Returns: { "user_id": 1, "role": "vendor", "session_token": "abc123..." }

POST /api/auth/logout
# Logout (invalidate session)
{ "session_token": "abc123..." }

GET /api/auth/validate?session_token=abc123
# Validate session and get user info
```

### Voice Conversation Flow

All voice endpoints now require a valid `session_token`:

```bash
POST /api/voice
{
  "session_token": "abc123...",
  "voice_text": "naya product add karo",
  "state": { "role": "vendor", "stage": "vendor_home" },
  "language": "hi"
}

POST /api/voice-audio
# Form data: session_token, state (JSON), language, audio_file
```

### Session Management

- **Session Timeout**: 24 hours of inactivity
- **Security**: Tokens are cryptographically secure random strings
- **Cleanup**: Expired sessions are automatically cleaned up
- **Multi-user**: Each user gets their own isolated data and context

---

## 🧭 Product Workflow

This is how a typical session flows end‑to‑end.

### 1. Choose role (landing screen)

1. User opens the web app at `http://localhost:5173/`.
2. First screen asks: **Continue as Vendor (विक्रेता)** or **Continue as Consumer (ग्राहक)**.
3. Based on the button they click, the frontend sets the role and opens the voice assistant screen.

### 2. Talk to the assistant (voice + Hindi text)

1. User presses the big mic button and speaks in Hindi.
2. Frontend records audio → sends it to `POST /api/voice-audio` along with:
     - `user_id` (demo: 1), `role` (vendor/consumer), and
     - `state` (previous `next_state` from backend).
3. Backend (main.py):
     - Uses `speech_utils.transcribe_audio_to_text` to convert audio → Hindi text (`user_text`).
     - Passes `user_text` + `state` into `handle_conversation` in `agents/conversation_agent.py`.
     - That function detects intent, runs the correct flow (vendor or consumer), reads/writes JSON in `/data`, and returns `reply_text`, `action`, `data`, and updated `next_state`.
     - Backend optionally generates Hindi speech audio from `reply_text` and returns `audio_base64`.
4. Frontend shows both:
     - **"आपकी बात"** = `user_text` (what STT heard), and
     - **"सारथी का जवाब"** = `reply_text` (assistant’s Hindi answer), and plays the audio.
5. Frontend stores `next_state` and sends it back on the next turn, so multi‑step flows continue naturally.

### 3. Vendor flows (examples)

- **Register shop** → `_vendor_register_shop` in `agents/conversation_agent.py`
    - Asks for shop name, then what items are sold; writes a new vendor into `data/vendors.json`.
- **Add product** → `_vendor_add_product`
    - Asks for product details by voice.
    - Uses `agents/listing_agent.extract_product` (Ollama + regex) to understand quantity, unit, price, freshness.
    - Confirms the details in Hindi, then writes a new item into `data/inventory.json`.
- **View orders** → `_vendor_view_orders`
    - Reads recent entries from `data/orders.json`.
    - Speaks and shows which consumer, address, quantity and product were ordered.
- **Udhar (credit)** → `_vendor_view_udhar`, `_vendor_mark_paid`, `_vendor_create_udhar`
    - Uses `agents/udhar_agent.py` and `data/udhar_ledger.json` / `data/pending_udhar.json` for creating and managing credit with full audit trail.

### 4. Consumer flows (examples)

- **Register user** → `_consumer_register`
    - Collects name and address; writes to `data/consumers.json`.
- **Search + compare vendors** → `_consumer_search_and_prepare_order`
    - Uses `agents/discovery_agent.search_products` to find matching inventory.
    - Compares multiple vendors (price, freshness, distance) and lets the user pick one by voice.
- **Place order** → `_consumer_choose_vendor_and_ask_qty` + `_consumer_place_order`
    - Asks for quantity, then writes an order into `data/orders.json` linking consumer and vendor.
- **View / pay udhar** → `_consumer_view_udhar`, `_consumer_pay_udhar`
    - Reads udhar info from `data/udhar_ledger.json` and pending requests from `data/pending_udhar.json`.
    - Guides the user through confirming or paying udhar using simple Hindi prompts.

## ✨ Key Technical Highlights

| Feature | Implementation |
|---------|---------------|
| Voice Input | Web Speech API, multi-language (en-IN) |
| LLM Integration | Ollama local models (phi3, etc.) |
| Fallback | Regex parser runs if API fails/unavailable |
| Audit Trail | Immutable append-only JSON log per transaction |
| Offline Mode | SMS command parser + USSD tree simulation |
| Compliance | Every udhar action timestamped and logged |
| No Hardcoded Keys | All secrets via `.env` variables |

## 📊 Business Impact

- **Time saved**: Vendor listing: 5 min → 30 sec voice input
- **Dispute reduction**: Immutable udhar audit trail eliminates "he said / she said"
- **Reach**: SMS fallback works on ₹500 feature phones, no smartphone needed
- **Discovery**: Buyers find best price/freshness in seconds vs. visiting multiple vendors