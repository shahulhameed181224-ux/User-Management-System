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


class DocumentType(str, enum.Enum):
    PATTA = "PATTA"
    SALE_DEED = "SALE_DEED"
    EC = "EC"
    LAYOUT_PLAN = "LAYOUT_PLAN"
    SETTLEMENT_DEED = "SETTLEMENT_DEED"


# Document Table
class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "property_services"}

    id = Column(Integer, primary_key=True, index=True)
    
    # Fully-qualified schema path to target table column
    property_code = Column(
        String(50),
        ForeignKey("property_services.properties.property_code", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    property_address = Column(Text, nullable=True)
    document_type = Column(SqlEnum(DocumentType), nullable=False)
    path_url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=False, default="Admin")
    updated_by = Column(String(100), nullable=True)

    # Document → Property relationship
    property = relationship("Property", back_populates="documents")


# User Table
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_service"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # USER DETAILS
    phone_number = Column(String(20), unique=True, nullable=False)
    role = Column(String(50))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    email_id = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    address = Column(Text)
    dob = Column(Date)
    bio_details = Column(Text)

    # TENANT DETAILS
    tenant_id = Column(UUID(as_uuid=True), nullable=True)
    tenant_name = Column(String(100))
    tenant_type = Column(String(20))
    tenant_created_by = Column(String(100))
    tenant_updated_by = Column(String(100))
    tenant_created_at = Column(DateTime(timezone=True))
    tenant_updated_at = Column(DateTime(timezone=True))

    # USER AUDIT DETAILS
    created_by = Column(String(100))
    updated_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # USER → PROPERTY
    properties = relationship("Property", back_populates="user")


# Property Table
class Property(Base):
    __tablename__ = "properties"
    __table_args__ = {"schema": "property_services"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_service.users.id"),
        nullable=False
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    property_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    property_name = Column(String(200), nullable=False)
    property_location = Column(Text)
    property_landmark = Column(String(255))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    area_size = Column(Numeric(10, 2))
    measurement_type = Column(String(30))
    plot_type = Column(String(30))
    ownership_type = Column(String(20))
    purchase_date = Column(Date)
    market_value = Column(Numeric(15, 2))
    description = Column(Text)
    verified_status = Column(String(20))
    risk_level = Column(String(20))
    fence_status = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_visited_at = Column(DateTime(timezone=True))
    remarks = Column(Text)
    visit_plan = Column(Text)
    photo_url = Column(Text)
    location_url = Column(Text)
    embedded_url = Column(Text)
    boundary_stones = Column(String(100))
    encroachment = Column(Boolean, default=False)
    legal_disputes = Column(Text)
    neighbour_issues = Column(Text)
    vegetation_issues = Column(Text)
    has_layout_plan = Column(Boolean, default=False)
    has_patta_chitta = Column(Boolean, default=False)
    latest_ec_date = Column(Date)
    service_required = Column(Text)
    additional_notes = Column(Text)
    land_owner_name = Column(String(200))
    source = Column(String(100))
    created_by = Column(String(100))
    updated_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="properties")
    documents = relationship("Document", back_populates="property", cascade="all, delete-orphan")