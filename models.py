import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import Date
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_service"}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    phone_number = Column(String(20))
    role = Column(String(50))
    full_name = Column(String(100))

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    email_id = Column(String(255))
    address = Column(Text)
    dob = Column(Date)
    bio_details = Column(Text)

    created_by = Column(String(100))
    updated_by = Column(String(100))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )