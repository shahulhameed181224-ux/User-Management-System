from typing import Optional

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
from enum import Enum

import phonenumbers
from pydantic import field_validator

from models import DocumentType

class DocumentBase(BaseModel):
    property_code: str
    property_address: Optional[str] = None
    document_type: DocumentType

class DocumentCreate(DocumentBase):
    path_url: str
    created_by: str

class DocumentResponse(DocumentBase):
    id: int
    path_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: str
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
# User Models        
class UserCreate(BaseModel):
    # USER DETAILS
    phone_number: str
    role: str
    full_name: str

    is_active: bool = True

    email_id: str
    password: str

    address: str | None = None
    dob: date | None = None
    bio_details: str | None = None
    # TENANT DETAILS
    tenant_id: UUID | None = None
    tenant_name: str

    tenant_type: str

    tenant_created_by: str | None = None
    tenant_updated_by: str | None = None

    tenant_created_at: datetime | None = None
    tenant_updated_at: datetime | None = None
    # USER AUDIT
    created_by: str
    updated_by: str | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value):

        try:

            phone = phonenumbers.parse(value, None)

            if not phonenumbers.is_valid_number(phone):
                raise ValueError("Invalid phone number")

            return phonenumbers.format_number(
                phone,
                phonenumbers.PhoneNumberFormat.E164
            )

        except Exception:
            raise ValueError("Invalid phone number")

class UserResponse(BaseModel):
    # USER DETAILS
    id: UUID
    full_name: str
    phone_number: str
    email_id: str
    role: str
    is_active: bool
    address: str | None = None
    dob: date | None = None
    bio_details: str | None = None

    # TENANT DETAILS
    tenant_id: UUID | None = None
    tenant_name: str | None = None
    tenant_type: str | None = None
    tenant_created_by: str | None = None
    tenant_updated_by: str | None = None

    # USER AUDIT
    created_by: str
    updated_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )

# Property Models
class PropertyCreate(BaseModel):

    user_id: UUID

    tenant_id: UUID

    property_code: str

    property_name: str

    property_location: Optional[str] = None

    property_landmark: Optional[str] = None

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    area_size: Optional[float] = None

    measurement_type: Optional[str] = None

    plot_type: Optional[str] = None

    ownership_type: Optional[str] = None

    purchase_date: Optional[date] = None

    market_value: Optional[Decimal] = None

    description: Optional[str] = None

    verified_status: Optional[str] = None

    risk_level: Optional[str] = None

    fence_status: bool = False

    is_active: bool = True

    last_visited_at: Optional[datetime] = None

    remarks: Optional[str] = None

    visit_plan: Optional[str] = None

    photo_url: Optional[str] = None

    location_url: Optional[str] = None

    embedded_url: Optional[str] = None

    boundary_stones: Optional[Decimal] = None

    encroachment: bool = False

    legal_disputes: Optional[str] = None

    neighbour_issues: Optional[str] = None

    vegetation_issues: Optional[str] = None

    has_layout_plan: bool = False

    has_patta_chitta: bool = False

    latest_ec_date: Optional[date] = None

    service_required: Optional[str] = None

    additional_notes: Optional[str] = None

    land_owner_name: Optional[str] = None

    source: Optional[str] = None

    created_by: str

    updated_by: Optional[str] = None

class PropertyResponse(BaseModel):
    id: UUID
    property_code: str
    property_name: str
    
    # User & Tenant
    user_id: Optional[UUID] = None
    user_name: Optional[str] = "No User"
    tenant_id: Optional[UUID] = None
    tenant_name: Optional[str] = "No Tenant"

    # Core details
    property_location: Optional[str] = None
    property_landmark: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_size: Optional[float] = None
    measurement_type: Optional[str] = None
    plot_type: Optional[str] = None
    ownership_type: Optional[str] = None
    purchase_date: Optional[date] = None
    market_value: Optional[float] = None
    verified_status: Optional[str] = "PENDING"
    risk_level: Optional[str] = None

    # Status Flags with defaults
    is_active: bool = True
    fence_status: Optional[bool] = False
    encroachment: Optional[bool] = False
    has_layout_plan: Optional[bool] = False
    has_patta_chitta: Optional[bool] = False

    # Inspection & Additional notes
    boundary_stones: Optional[int] = None
    latest_ec_date: Optional[date] = None
    land_owner_name: Optional[str] = None
    source: Optional[str] = None
    last_visited_at: Optional[datetime] = None
    photo_url: Optional[str] = None
    location_url: Optional[str] = None
    embedded_url: Optional[str] = None
    description: Optional[str] = None
    remarks: Optional[str] = None
    visit_plan: Optional[str] = None
    legal_disputes: Optional[str] = None
    neighbour_issues: Optional[str] = None
    vegetation_issues: Optional[str] = None
    service_required: Optional[str] = None
    additional_notes: Optional[str] = None
    
    # Audit
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PropertyUpdate(PropertyCreate):
    pass

# USER PROPERTY SUMMARY

class UserPropertySummary(BaseModel):

    user_id: UUID

    user_name: str

    tenant_id: UUID | None = None

    tenant_name: str | None = None

    property_count: int

    properties: list[PropertyResponse]

    model_config = ConfigDict(
        from_attributes=True
    )

# TENANT PROPERTY SUMMARY

class TenantPropertySummary(BaseModel):

    tenant_id: UUID

    tenant_name: str

    property_count: int

    properties: list[PropertyResponse]

    model_config = ConfigDict(
        from_attributes=True
    )

class TenantSummary(BaseModel):
    tenant_id: UUID
    tenant_name: str
    user_count: int
    property_count: int
    model_config = ConfigDict(
        from_attributes=True
    )

class UserPropertyCount(BaseModel):
    user_id: UUID
    user_name: str
    tenant_id: UUID | None = None
    tenant_name: str | None = None
    property_count: int
    model_config = ConfigDict(
        from_attributes=True
    )
