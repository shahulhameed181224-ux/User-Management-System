import uuid
import enum

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Integer,
    Enum as SqlEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


# ENUMS

class TenantType(str, enum.Enum):
    SINGLE = "SINGLE"
    GROUP = "GROUP"
    COMMERCIAL = "COMMERCIAL"


class DocumentType(str, enum.Enum):
    PATTA = "PATTA"
    SALE_DEED = "SALE_DEED"
    EC = "EC"
    LAYOUT_PLAN = "LAYOUT_PLAN"
    SETTLEMENT_DEED = "SETTLEMENT_DEED"


# TABLE 1: TENANTS

class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "user_service"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    tenant_name = Column(String(100), unique=True, nullable=False, index=True)
    tenant_type = Column(
        SqlEnum(TenantType, name="tenant_type_enum", create_type=False),
        nullable=False,
        default=TenantType.SINGLE
    )
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="tenant", cascade="all, delete-orphan")


# TABLE 2: USERS

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_service"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign Key linking to Tenant
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_service.tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Unique username used for property linking
    user_name = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email_id = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="User")
    is_active = Column(Boolean, default=True)
    address = Column(Text, nullable=True)
    dob = Column(Date, nullable=True)
    bio_details = Column(Text, nullable=True)

    # Audit Details
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    properties = relationship("Property", back_populates="user", cascade="all, delete-orphan")


# TABLE 3: PROPERTIES

class Property(Base):
    __tablename__ = "properties"
    __table_args__ = {"schema": "property_services"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Direct linkage via user_name
    user_name = Column(
        String(100),
        ForeignKey("user_service.users.user_name", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_service.tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    property_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    property_name = Column(String(200), nullable=False)
    property_location = Column(Text, nullable=True)
    property_landmark = Column(String(255), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    area_size = Column(Numeric(10, 2), nullable=True)
    measurement_type = Column(String(30), nullable=True)
    plot_type = Column(String(30), nullable=True)
    ownership_type = Column(String(20), nullable=True)
    purchase_date = Column(Date, nullable=True)
    market_value = Column(Numeric(15, 2), nullable=True)
    description = Column(Text, nullable=True)
    verified_status = Column(String(20), default="PENDING")
    risk_level = Column(String(20), default="LOW")
    fence_status = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_visited_at = Column(DateTime(timezone=True), nullable=True)
    remarks = Column(Text, nullable=True)
    visit_plan = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)
    location_url = Column(Text, nullable=True)
    embedded_url = Column(Text, nullable=True)
    boundary_stones = Column(String(100), nullable=True)
    encroachment = Column(Boolean, default=False)
    legal_disputes = Column(Text, nullable=True)
    neighbour_issues = Column(Text, nullable=True)
    vegetation_issues = Column(Text, nullable=True)
    has_layout_plan = Column(Boolean, default=False)
    has_patta_chitta = Column(Boolean, default=False)
    latest_ec_date = Column(Date, nullable=True)
    service_required = Column(Text, nullable=True)
    additional_notes = Column(Text, nullable=True)
    land_owner_name = Column(String(200), nullable=True)
    source = Column(String(100), nullable=True)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="properties")
    tenant = relationship("Tenant", back_populates="properties")
    documents = relationship("Document", back_populates="property", cascade="all, delete-orphan")


# TABLE 4: DOCUMENTS

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "property_services"}

    id = Column(Integer, primary_key=True, index=True)
    
    property_code = Column(
        String(50),
        ForeignKey("property_services.properties.property_code", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    property_address = Column(Text, nullable=True)
    document_type = Column(SqlEnum(DocumentType, name="document_type_enum", create_type=False), nullable=False)
    path_url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=False, default="Admin")
    updated_by = Column(String(100), nullable=True)

    # Document → Property relationship
    property = relationship("Property", back_populates="documents")