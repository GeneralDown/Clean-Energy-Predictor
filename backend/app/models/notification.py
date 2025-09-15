"""
Notification subscription models for the Clean Energy Predictor.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum as SQLEnum, Index, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
import uuid

class NotificationMethod(str, Enum):
    """Notification delivery methods."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class NotificationSubscriptionDB(Base):
    """SQLAlchemy model for notification subscriptions."""
    __tablename__ = "notification_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), nullable=False, index=True)
    location = Column(String(100), nullable=False, index=True)
    method = Column(SQLEnum(NotificationMethod), nullable=False, default=NotificationMethod.EMAIL)
    threshold_score = Column(Float, nullable=False, default=70.0, comment="Minimum cleanliness score to trigger notification")
    advance_hours = Column(Float, nullable=False, default=1.0, comment="Hours in advance to send notification")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    timezone = Column(String(50), nullable=False, default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    last_notification_sent = Column(DateTime(timezone=True), nullable=True)
    
    # Constraints and indexes
    __table_args__ = (
        CheckConstraint('threshold_score >= 0 AND threshold_score <= 100', name='check_threshold_score'),
        CheckConstraint('advance_hours >= 0 AND advance_hours <= 24', name='check_advance_hours'),
        Index('idx_notif_email_location', 'email', 'location'),
        Index('idx_notif_active_location', 'is_active', 'location'),
        Index('idx_notif_created_at', 'created_at'),
    )

class NotificationSubscription(BaseModel):
    """Pydantic model for notification subscription validation."""
    email: EmailStr
    location: str = Field(..., max_length=100)
    method: NotificationMethod = NotificationMethod.EMAIL
    threshold_score: float = Field(70.0, ge=0, le=100, description="Minimum cleanliness score to trigger notification")
    advance_hours: float = Field(1.0, ge=0, le=24, description="Hours in advance to send notification")
    timezone: str = Field("UTC", max_length=50)

class NotificationSubscriptionCreate(NotificationSubscription):
    """Model for creating new notification subscriptions."""
    pass

class NotificationSubscriptionUpdate(BaseModel):
    """Model for updating notification subscriptions."""
    method: Optional[NotificationMethod] = None
    threshold_score: Optional[float] = Field(None, ge=0, le=100)
    advance_hours: Optional[float] = Field(None, ge=0, le=24)
    is_active: Optional[bool] = None
    timezone: Optional[str] = Field(None, max_length=50)

class NotificationSubscriptionResponse(NotificationSubscription):
    """Response model including database fields."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_notification_sent: Optional[datetime]
    
    class Config:
        from_attributes = True

class NotificationLogDB(Base):
    """SQLAlchemy model for notification delivery logs."""
    __tablename__ = "notification_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    subscription_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    method = Column(SQLEnum(NotificationMethod), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255))
    message = Column(String(1000))
    status = Column(String(50), nullable=False, default="sent")
    error_message = Column(String(500), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_log_subscription_sent', 'subscription_id', 'sent_at'),
        Index('idx_log_sent_desc', 'sent_at', postgresql_using='btree', postgresql_ops={'sent_at': 'DESC'}),
        Index('idx_log_status', 'status'),
    )

class NotificationLog(BaseModel):
    """Pydantic model for notification logs."""
    subscription_id: str
    method: NotificationMethod
    recipient: str
    subject: Optional[str] = None
    message: Optional[str] = None
    status: str = "sent"
    error_message: Optional[str] = None

class NotificationLogResponse(NotificationLog):
    """Response model for notification logs."""
    id: str
    sent_at: datetime
    
    class Config:
        from_attributes = True