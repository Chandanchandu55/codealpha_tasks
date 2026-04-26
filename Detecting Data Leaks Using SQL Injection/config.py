import os
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet
import base64

class Settings(BaseSettings):
    database_url: str = "sqlite:///./sql_injection_security.db"
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "your-32-byte-encryption-key-here"
    capability_secret: str = "capability-secret-key"
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Generate encryption key from settings
def get_encryption_key():
    """Generate or derive encryption key"""
    if len(settings.encryption_key) == 44:  # Base64 encoded key
        return settings.encryption_key.encode()
    else:
        # Generate a key from the provided string
        return base64.urlsafe_b64encode(settings.encryption_key.encode().ljust(32, b'0')[:32])

# Initialize encryption
encryption_cipher = Fernet(get_encryption_key())

# Capability code settings
CAPABILITY_CODE_LENGTH = 32
CAPABILITY_EXPIRE_MINUTES = 60
