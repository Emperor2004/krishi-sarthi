"""Exceptions package for Krishi Saarthi."""
from .custom import (
    KrishiException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    DatabaseError,
    ExternalServiceError,
    BusinessLogicError,
    RateLimitError,
    ConfigurationError
)

__all__ = [
    "KrishiException",
    "AuthenticationError",
    "AuthorizationError", 
    "ValidationError",
    "DatabaseError",
    "ExternalServiceError",
    "BusinessLogicError",
    "RateLimitError",
    "ConfigurationError"
]
