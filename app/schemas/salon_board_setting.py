"""SALON BOARD setting Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


# Base schema with common attributes
class SalonBoardSettingBase(BaseModel):
    """Base SALON BOARD setting schema with common attributes."""

    setting_name: str = Field(..., min_length=1, max_length=100)
    sb_user_id: str = Field(..., min_length=1, max_length=255)
    salon_id: str | None = Field(None, max_length=100)
    salon_name: str | None = Field(None, max_length=255)


# Schema for setting creation (request)
class SalonBoardSettingCreate(SalonBoardSettingBase):
    """Schema for creating a new SALON BOARD setting."""

    sb_password: str = Field(..., min_length=1, max_length=255, description="Plain text password (will be encrypted)")


# Schema for setting update (request)
class SalonBoardSettingUpdate(BaseModel):
    """Schema for updating a SALON BOARD setting."""

    setting_name: str | None = Field(None, min_length=1, max_length=100)
    sb_user_id: str | None = Field(None, min_length=1, max_length=255)
    sb_password: str | None = Field(None, min_length=1, max_length=255, description="Plain text password (will be encrypted)")
    salon_id: str | None = Field(None, max_length=100)
    salon_name: str | None = Field(None, max_length=255)


# Schema for setting in database (response)
class SalonBoardSettingInDB(SalonBoardSettingBase):
    """Schema for SALON BOARD setting stored in database."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Schema for setting response (public - excludes encrypted password)
class SalonBoardSetting(SalonBoardSettingInDB):
    """Schema for SALON BOARD setting response (excludes password)."""

    pass
