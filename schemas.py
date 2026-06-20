from pydantic import BaseModel
from datetime import date
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    phone_number: str
    role: str
    full_name: str

    tenant_id: UUID | None = None

    is_active: bool = True

    email_id: str | None = None
    address: str | None = None
    dob: date | None = None
    bio_details: str | None = None

    created_by: str
    updated_by: str | None = None


class UserResponse(UserCreate):
    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True