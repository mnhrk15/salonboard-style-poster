"""Security utilities for password hashing, encryption, and JWT tokens."""

from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption (AES-256 via Fernet)
# Ensure ENCRYPTION_KEY is a valid 32-byte base64-encoded key
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
try:
    cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())
except Exception as e:
    raise ValueError(
        f"Invalid ENCRYPTION_KEY. Must be a valid Fernet key (32 bytes, base64-encoded): {e}"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string.
    """
    return pwd_context.hash(password)


def encrypt_password(plain_password: str) -> str:
    """Encrypt a password using AES-256 (Fernet).

    Args:
        plain_password: Plain text password to encrypt.

    Returns:
        Encrypted password as a string.
    """
    encrypted_bytes = cipher_suite.encrypt(plain_password.encode())
    return encrypted_bytes.decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt an encrypted password.

    Args:
        encrypted_password: Encrypted password string.

    Returns:
        Decrypted plain text password.

    Raises:
        Exception: If decryption fails.
    """
    decrypted_bytes = cipher_suite.decrypt(encrypted_password.encode())
    return decrypted_bytes.decode()


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: Dictionary of data to encode in the token (e.g., {"sub": user_email}).
        expires_delta: Optional expiration time delta. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT access token.

    Args:
        token: JWT token string to decode.

    Returns:
        Decoded token payload as a dictionary, or None if invalid.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
