from typing import Optional, List, Union
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal
import phonenumbers

from models import DocumentType, TenantType


# TENANT SCHEMAS

class TenantBase(BaseModel):
    tenant_name: str
    tenant_type: TenantType = TenantType.SINGLE


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantBase):
    id: UUID
    property_count: int = 0
    user_count: int = 0
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TenantCheckResponse(BaseModel):
    exists: bool
    tenant: Optional[TenantResponse] = None
    user_count: int
    property_count: int
    allow_new_user: bool
    allow_new_property: bool


# DOCUMENT SCHEMAS

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

    model_config = ConfigDict(from_attributes=True)


# USER SCHEMAS

class UserCreate(BaseModel):
    tenant_id: UUID
    user_name: Optional[str] = None
    full_name: str
    email_id: str
    phone_number: str
    password: str
    role: str = "User"
    is_active: bool = True
    address: Optional[str] = None
    dob: Optional[date] = None
    bio_details: Optional[str] = None
    created_by: str = "Admin"
    updated_by: Optional[str] = None

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
    id: UUID
    tenant_id: UUID
    tenant_name: Optional[str] = None
    tenant_type: Optional[str] = None
    user_name: str
    full_name: str
    phone_number: str
    email_id: str
    role: str
    is_active: bool
    address: Optional[str] = None
    dob: Optional[date] = None
    bio_details: Optional[str] = None
    property_count: int = 0
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# PROPERTY SCHEMAS

class PropertyCreate(BaseModel):
    user_name: str
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
    verified_status: Optional[str] = "PENDING"
    risk_level: Optional[str] = "LOW"
    fence_status: bool = False
    is_active: bool = True
    last_visited_at: Optional[datetime] = None
    remarks: Optional[str] = None
    visit_plan: Optional[str] = None
    photo_url: Optional[str] = None
    location_url: Optional[str] = None
    embedded_url: Optional[str] = None

    # Fixed: accepts string, int, or float from db/form
    boundary_stones: Optional[Union[str, int, float]] = None

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
    created_by: str = "Admin"
    updated_by: Optional[str] = None

    @field_validator("boundary_stones", mode="before")
    @classmethod
    def coerce_boundary_stones_create(cls, v):
        return str(v) if v is not None else None


class PropertyUpdate(PropertyCreate):
    pass


class PropertyResponse(BaseModel):
    id: UUID
    property_code: str
    property_name: str
    user_name: str
    tenant_id: UUID
    tenant_name: Optional[str] = "No Tenant"
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
    is_active: bool = True
    fence_status: Optional[bool] = False
    encroachment: Optional[bool] = False
    has_layout_plan: Optional[bool] = False
    has_patta_chitta: Optional[bool] = False

    # Fixed: accepts string, int, or float from db and converts to string
    boundary_stones: Optional[Union[str, int, float]] = None

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
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("boundary_stones", mode="before")
    @classmethod
    def coerce_boundary_stones_response(cls, v):
        return str(v) if v is not None else None


# SUMMARY & AGGREGATION SCHEMAS

class UserPropertySummary(BaseModel):
    user_name: str
    tenant_id: UUID | None = None
    tenant_name: str | None = None
    property_count: int
    properties: List[PropertyResponse]

    model_config = ConfigDict(from_attributes=True)


class TenantPropertySummary(BaseModel):
    tenant_id: UUID
    tenant_name: str
    property_count: int
    properties: List[PropertyResponse]

    model_config = ConfigDict(from_attributes=True)


class TenantSummary(BaseModel):
    tenant_id: UUID
    tenant_name: str
    tenant_type: Optional[str] = None
    user_count: int
    property_count: int

    model_config = ConfigDict(from_attributes=True)


class UserPropertyCount(BaseModel):
    user_name: str
    full_name: str
    tenant_id: UUID | None = None
    tenant_name: str | None = None
    property_count: int

    model_config = ConfigDict(from_attributes=True)