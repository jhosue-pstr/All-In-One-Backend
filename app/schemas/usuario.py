from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    correo: EmailStr
    nombre: str
    apellido: str


class UserCreate(UserBase):
    contrasena: str


class UserLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
