"""Enhanced configuration management with environment-specific settings."""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    password_min_length: int = 8
    login_rate_limit: int = 5
    login_window_minutes: int = 300
    api_rate_limit: int = 100
    api_window_seconds: int = 60


@dataclass
class LLMConfig:
    """LLM service configuration."""
    ollama_host: str
    ollama_model: str = "phi3:latest"
    ollama_model_conversation: Optional[str] = None
    ollama_model_listing: Optional[str] = None
    ollama_model_discovery: Optional[str] = None
    request_timeout: int = 60
    max_retries: int = 2
    cache_enabled: bool = True
    cache_ttl: int = 300


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"
    log_file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    metrics_enabled: bool = True
    health_check_enabled: bool = True
    alerting_enabled: bool = True
    metrics_retention_hours: int = 24
    performance_profiling: bool = False


@dataclass
class AppConfig:
    """Main application configuration."""
    environment: Environment
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    database: DatabaseConfig
    security: SecurityConfig
    llm: LLMConfig
    logging: LoggingConfig
    monitoring: MonitoringConfig


class ConfigManager:
    """Manages application configuration from environment and files."""
    
    @staticmethod
    def load_config() -> AppConfig:
        """Load configuration from environment variables."""
        env = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value)
        environment = Environment(env)
        
        # Database configuration
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///./krishi_sarthi.db"
        )
        
        database = DatabaseConfig(
            url=database_url,
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600"))
        )
        
        # Security configuration
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret:
            if environment == Environment.PRODUCTION:
                raise ValueError("JWT_SECRET_KEY must be set in production")
            jwt_secret = "dev-secret-key-change-in-production"
        
        security = SecurityConfig(
            jwt_secret_key=jwt_secret,
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "1440")),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            login_rate_limit=int(os.getenv("LOGIN_RATE_LIMIT", "5")),
            login_window_minutes=int(os.getenv("LOGIN_WINDOW_MINUTES", "300")),
            api_rate_limit=int(os.getenv("API_RATE_LIMIT", "100")),
            api_window_seconds=int(os.getenv("API_WINDOW_SECONDS", "60"))
        )
        
        # LLM configuration
        llm = LLMConfig(
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "phi3:latest"),
            ollama_model_conversation=os.getenv("OLLAMA_MODEL_CONVERSATION"),
            ollama_model_listing=os.getenv("OLLAMA_MODEL_LISTING"),
            ollama_model_discovery=os.getenv("OLLAMA_MODEL_DISCOVERY"),
            request_timeout=int(os.getenv("LLM_REQUEST_TIMEOUT", "60")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
            cache_enabled=os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("LLM_CACHE_TTL", "300"))
        )
        
        # Logging configuration
        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "json"),
            log_file=os.getenv("LOG_FILE"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )
        
        # Monitoring configuration
        monitoring = MonitoringConfig(
            metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
            health_check_enabled=os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true",
            alerting_enabled=os.getenv("ALERTING_ENABLED", "true").lower() == "true",
            metrics_retention_hours=int(os.getenv("METRICS_RETENTION_HOURS", "24")),
            performance_profiling=os.getenv("PERFORMANCE_PROFILING", "false").lower() == "true"
        )
        
        # Application configuration
        debug = environment != Environment.PRODUCTION and os.getenv("DEBUG", "false").lower() == "true"
        
        return AppConfig(
            environment=environment,
            debug=debug,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            database=database,
            security=security,
            llm=llm,
            logging=logging_config,
            monitoring=monitoring
        )
    
    @staticmethod
    def get_cors_origins() -> list:
        """Get CORS origins based on environment."""
        env = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT.value)
        
        if env == Environment.PRODUCTION.value:
            return [
                "https://krishi-sarthi.example.com",
                "https://www.krishi-sarthi.example.com"
            ]
        elif env == Environment.STAGING.value:
            return [
                "https://staging.krishi-sarthi.example.com",
                "http://localhost:3000"
            ]
        else:  # Development
            return [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ]
    
    @staticmethod
    def validate_config(config: AppConfig) -> Dict[str, Any]:
        """Validate configuration and return any issues."""
        issues = []
        
        # Validate database
        if not config.database.url:
            issues.append("Database URL is required")
        
        # Validate security
        if len(config.security.jwt_secret_key) < 32:
            issues.append("JWT secret key should be at least 32 characters")
        
        # Validate LLM
        if not config.llm.ollama_host:
            issues.append("Ollama host is required")
        
        # Validate ports
        if not (1 <= config.port <= 65535):
            issues.append("Port must be between 1 and 65535")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


# Global configuration instance
config = ConfigManager.load_config()
config_validation = ConfigManager.validate_config(config)
