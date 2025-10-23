"""User Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# Base schema with common attributes
class UserBase(BaseModel):
    """Base user schema with common attributes."""

    email: EmailStr


# Schema for user creation (request)
class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="user", pattern="^(admin|user)$")


# Schema for user update (request)
class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=128)
    role: str | None = Field(None, pattern="^(admin|user)$")
    is_active: bool | None = None


# Schema for user in database (response)
class UserInDB(UserBase):
    """Schema for user stored in database."""

    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Schema for user response (public)
class User(UserInDB):
    """Schema for user response (excludes sensitive data)."""

    pass


# Schema for authentication token
class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


# Schema for token payload
class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str | None = None  # subject (user email)
    exp: int | None = None  # expiration time
