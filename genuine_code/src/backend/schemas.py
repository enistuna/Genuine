from pydantic import BaseModel, validator, Field
from typing import List, Optional
from decimal import Decimal

class UserBase(BaseModel):
    username: str
    full_name: str
    tckn: str

    @validator('tckn')
    def validate_tckn(cls, v):
        if len(v) != 11 or not v.isdigit() or v.startswith('0'):
            raise ValueError('TCKN must be 11 digits and cannot start with 0')
        
        digits = [int(d) for d in v]
        
        sum_odd = sum(digits[0:9:2])
        sum_even = sum(digits[1:8:2])
        d10 = ((sum_odd * 7) - sum_even) % 10
        d11 = sum(digits[:10]) % 10

        
        if d10 != digits[9]:
            raise ValueError('Invalid TCKN checksum (10th digit)')
            
        if d11 != digits[10]:
            raise ValueError('Invalid TCKN checksum (11th digit)')
            
        return v

class TransactionBase(BaseModel):
    amount: Decimal
    description: str

class TransferRequest(BaseModel):
    sender_tckn: str
    recipient_tckn: str
    amount: Decimal

    class Config:
        schema_extra = {
            "example": {
                "sender_tckn": "10000000146",
                "recipient_tckn": "10000000254",
                "amount": 150.50
            }
        }

class UserProfileBase(BaseModel):
    interaction_count: int = 0
    financial_literacy_score: int = 50
    preferred_tone: str = "formal"
    last_topic: Optional[str] = None

class UserProfileUpdate(BaseModel):
    topic: str
    sentiment: str
    used_slang: bool

class UserResponse(UserBase):
    user_id: int
    balance: Decimal
    profile: Optional[UserProfileBase] = None