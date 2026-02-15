import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_validation(cls, v: str) -> str:
        # 8文字以上
        if len(v) < 8:
            raise ValueError('パスワードは8文字以上である必要があります')
        # 英数字混在（2026年の最低限のセキュリティ基準）
        if not re.search(r'[A-Za-z]', v) or not re.search(r'[0-9]', v):
            raise ValueError('パスワードには英字と数字の両方を含める必要があります')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)