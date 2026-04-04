from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl


class CreateUserSchema(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(str_strip_whitespace=True)


class UpdateUserSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class CreateUrlSchema(BaseModel):
    user_id: int
    original_url: HttpUrl
    title: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)


class UpdateUrlSchema(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(str_strip_whitespace=True)
