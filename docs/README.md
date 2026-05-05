# Krishi Saarthi Documentation

## Overview

Krishi Saarthi is a voice-first AI system for rural agricultural commerce in India. It enables farmers and consumers to interact with agricultural marketplaces using natural Hindi speech.

## Architecture

### Backend (FastAPI)
- **Core Engine**: Conversation management and intent detection
- **Services**: Domain-specific business logic (listing, discovery, payments)
- **Utils**: Shared utilities and data management
- **Authentication**: Session-based user management

### Frontend (Vanilla JS + Vite)
- **Authentication**: Login/register screens
- **Voice Interface**: Web Speech API integration
- **Real-time**: Live conversation with AI assistant

## API Reference

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/validate` - Validate session

### Voice Endpoints
- `POST /api/voice` - Text-based conversation
- `POST /api/voice-audio` - Audio-based conversation

### Business Endpoints
- `POST /api/listing` - Add product listing
- `POST /api/discovery` - Search products
- `POST /api/udhar/*` - Credit management

## Development

### Setup
```bash
# Run setup script
python scripts/dev.py setup

# Or manually
python scripts/setup.py
```

### Running
```bash
# Backend
python scripts/dev.py backend

# Frontend (separate terminal)
python scripts/dev.py frontend
```

### Testing
```bash
python scripts/dev.py test
```

## Deployment

### Production Setup
1. Configure environment variables
2. Set up Ollama with required models
3. Run with production ASGI server (uvicorn/gunicorn)
4. Configure reverse proxy (nginx)

### Environment Variables
- `OLLAMA_HOST` - Ollama server URL
- `OLLAMA_MODEL` - Model name (default: phi3:latest)
- `ENVIRONMENT` - Set to "production" for prod mode

## Contributing

### Code Organization
- `src/krishi/core/` - Core business logic
- `src/krishi/services/` - Domain services
- `src/krishi/utils/` - Shared utilities
- `tests/` - Test suite
- `scripts/` - Development scripts
- `docs/` - Documentation

### Coding Standards
- Use type hints
- Follow PEP 8
- Add docstrings
- Write tests for new features

## Troubleshooting

### Common Issues
1. **Ollama connection failed**: Ensure Ollama is running and accessible
2. **STT/TTS not working**: Check optional dependencies installation
3. **Session expired**: User needs to re-authenticate
4. **Import errors**: Run from project root directory

### Logs
- Backend logs to console with `uvicorn`
- Check browser console for frontend issues
- Ollama logs in Ollama application