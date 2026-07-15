from typing import Optional

from pydantic import BaseModel
from datetime import date
from datetime import datetime
from uuid import UUID

from enum import Enum

import phonenumbers
from pydantic import field_validator

class TenantType(str, Enum):
    GROUP="GROUP"
    INDIVIDUAL="INDIVIDUAL"
    ENTERPRISE="ENTERPRISE"

class TenantCreate(BaseModel):
    tenant_name: str
    tenant_type: TenantType
    created_by: str
    updated_by: str | None = None

class TenantResponse(BaseModel):
    id: UUID
    tenant_name: str
    tenant_type: str
    created_by: str
    updated_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
        
class UserCreate(BaseModel):
    phone_number: str        
    role: str
    full_name: str

    tenant_id: Optional[UUID] = None
    tenant_name: Optional[str] = None

    is_active: bool = True

    email_id: str 
    password: str

    address: str | None = None
    dob: date | None = None
    bio_details: str | None = None

    created_by: str
    updated_by: str | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):
        try:
            phone=phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(phone):
                raise ValueError("Invalid phone number")
            
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except:
            raise ValueError("Invalid phone number")


class UserResponse(BaseModel):
    id: UUID

    phone_number: str
    role: str
    full_name: str

    tenant_id: UUID | None = None
    tenant_name: str | None = None

    is_active: bool

    email_id: str
    address: str | None = None
    dob: date | None = None
    bio_details: str | None = None

    created_by: str
    updated_by: str | None = None
    
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True