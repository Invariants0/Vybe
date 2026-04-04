from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl, field_validator
import re


class CreateUserSchema(BaseModel):
    username: str
    email: str

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format - more permissive than EmailStr to allow .local domains."""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('value is not a valid email address: An email address must have an @-sign.')
        return v


class UpdateUserSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format - more permissive than EmailStr to allow .local domains."""
        if v is not None and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('value is not a valid email address: An email address must have an @-sign.')
        return v


class CreateUrlSchema(BaseModel):
    user_id: int
    original_url: HttpUrl
    title: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('original_url')
    @classmethod
    def convert_url_to_string(cls, v: HttpUrl) -> str:
        """Convert HttpUrl to string to avoid trailing slash issues."""
        return str(v).rstrip('/')


class UpdateUrlSchema(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True)
