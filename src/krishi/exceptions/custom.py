"""Custom exceptions for Krishi Saarthi."""
from typing import Optional, Any, Dict


class KrishiException(Exception):
    """Base exception for Krishi Saarthi application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(KrishiException):
    """Authentication related errors."""
    pass


class AuthorizationError(KrishiException):
    """Authorization related errors."""
    pass


class ValidationError(KrishiException):
    """Data validation errors."""
    pass


class DatabaseError(KrishiException):
    """Database operation errors."""
    pass


class ExternalServiceError(KrishiException):
    """External service (LLM, etc.) errors."""
    pass


class BusinessLogicError(KrishiException):
    """Business logic validation errors."""
    pass


class RateLimitError(KrishiException):
    """Rate limiting errors."""
    pass


class ConfigurationError(KrishiException):
    """Configuration related errors."""
    pass
