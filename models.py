import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


# Tenant Table
class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "user_service"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_name = Column(
        String(100),
        nullable=False
    )

    tenant_type = Column(
        String(20),
        nullable=False
    )

    created_by = Column(
        String(100),
        nullable=False
    )

    updated_by = Column(
        String(100)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # One Tenant -> Many Users
    users = relationship(
        "User",
        back_populates="tenant"
    )


# User Table
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_service"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    phone_number = Column(
        String(20)
    )

    role = Column(
        String(50)
    )

    full_name = Column(
        String(100)
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_service.tenants.id"),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    email_id = Column(
        String(255)
    )

    address = Column(
        Text
    )

    dob = Column(
        Date
    )

    bio_details = Column(
        Text
    )

    created_by = Column(
        String(100)
    )

    updated_by = Column(
        String(100)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Many Users -> One Tenant
    tenant = relationship(
        "Tenant",
        back_populates="users"
    )