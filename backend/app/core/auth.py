"""
Authentication and authorization system
"""
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timedelta

from .config import settings

# API Key security scheme
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


class APIKeyManager:
    """
    Simple API key manager for authentication

    In production, this should be replaced with a database-backed
    system with proper user management.
    """

    def __init__(self):
        # For MVP, we'll use environment-based API keys
        # In production, store these in database with user associations
        self.valid_keys = self._load_api_keys()

    def _load_api_keys(self) -> set:
        """Load valid API keys from environment"""
        # Check for environment variable with comma-separated keys
        env_keys = os.getenv("API_KEYS", "")
        if env_keys:
            return set(key.strip() for key in env_keys.split(",") if key.strip())

        # For development, generate a default key
        if settings.ENVIRONMENT == "development":
            default_key = "dev_" + secrets.token_urlsafe(32)
            print(f"🔑 Development API Key: {default_key}")
            return {default_key}

        return set()

    def generate_api_key(self, prefix: str = "mk") -> str:
        """
        Generate a new API key

        Args:
            prefix: Key prefix (e.g., 'mk' for Moments Key)

        Returns:
            New API key in format: prefix_randomsecret
        """
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"

    def hash_key(self, api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def validate_key(self, api_key: str) -> bool:
        """
        Validate an API key

        Args:
            api_key: The API key to validate

        Returns:
            True if valid, False otherwise
        """
        if not api_key:
            return False

        # In development mode with no keys configured, allow all
        if settings.ENVIRONMENT == "development" and not self.valid_keys:
            return True

        return api_key in self.valid_keys

    def add_key(self, api_key: str):
        """Add a new valid API key"""
        self.valid_keys.add(api_key)

    def remove_key(self, api_key: str):
        """Remove an API key"""
        self.valid_keys.discard(api_key)


# Global API key manager instance
api_key_manager = APIKeyManager()


# Import os at the top
import os


async def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Dependency to validate API key from header

    Usage:
        @app.get("/protected")
        async def protected_route(api_key: str = Depends(get_api_key)):
            return {"message": "Authorized"}

    Raises:
        HTTPException: If API key is missing or invalid
    """

    # In development without keys, allow access
    if settings.ENVIRONMENT == "development" and not api_key_manager.valid_keys:
        return "development-access"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not api_key_manager.validate_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key


async def get_optional_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[str]:
    """
    Optional API key dependency - doesn't raise error if missing
    Useful for endpoints that work with or without authentication
    """
    if api_key and api_key_manager.validate_key(api_key):
        return api_key
    return None


# Rate limiting store (simple in-memory for MVP)
# In production, use Redis
class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = {}  # {key: [(timestamp, count), ...]}

    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit

        Args:
            identifier: Unique identifier (API key, IP, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            (allowed, remaining): Tuple of (bool, int)
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                ts for ts in self.requests[identifier] if ts > cutoff
            ]
        else:
            self.requests[identifier] = []

        # Check limit
        current_count = len(self.requests[identifier])

        if current_count >= max_requests:
            return False, 0

        # Add new request
        self.requests[identifier].append(now)

        remaining = max_requests - current_count - 1
        return True, remaining


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(
    api_key: str = Depends(get_api_key),
) -> str:
    """
    Dependency to check rate limit

    Raises:
        HTTPException: If rate limit exceeded
    """
    if not settings.RATE_LIMIT_ENABLED:
        return api_key

    # Check per-minute limit
    allowed, remaining = rate_limiter.check_rate_limit(
        identifier=api_key,
        max_requests=settings.RATE_LIMIT_PER_MINUTE,
        window_seconds=60
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"},
        )

    return api_key


# Helper function to generate API keys for users
def generate_user_api_key(user_id: str) -> str:
    """
    Generate API key for a user

    In production, this should:
    1. Store in database with user_id association
    2. Hash the key before storage
    3. Return unhashed key to user (only time they see it)
    """
    api_key = api_key_manager.generate_api_key()

    # TODO: Store in database
    # await db.execute(
    #     "INSERT INTO api_keys (key_hash, user_id, created_at) VALUES (?, ?, ?)",
    #     (api_key_manager.hash_key(api_key), user_id, datetime.utcnow())
    # )

    return api_key
