
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# User Registration Schema
class UserCreate(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


# User Login Schema
class UserLogin(BaseModel):

    email: EmailStr

    password: str


# User Response Schema
class UserResponse(BaseModel):

    user_id: int

    full_name: str

    email: EmailStr

    role: Literal["candidate", "hr"]

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

