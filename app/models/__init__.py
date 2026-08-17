from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    ADMIN = "admin"
    JOURNALIST = "journalist"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)

    author = relationship("User")


class Fighter(Base):
    __tablename__ = "fighters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    odds = relationship("OddsRecord", back_populates="fighter")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    promotion = Column(String, index=True, nullable=False)
    fighter_a_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    fighter_b_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    event_date = Column(String, nullable=True)

    fighter_a = relationship("Fighter", foreign_keys=[fighter_a_id])
    fighter_b = relationship("Fighter", foreign_keys=[fighter_b_id])
    odds = relationship("OddsRecord", back_populates="event")


class OddsRecord(Base):
    __tablename__ = "odds_records"

    id = Column(Integer, primary_key=True, index=True)
    fighter_id = Column(Integer, ForeignKey("fighters.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    sportsbook = Column(String, nullable=False)
    fighter1_odds = Column(Float, nullable=False)
    fighter2_odds = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=utcnow, nullable=False)

    fighter = relationship("Fighter", back_populates="odds")
    event = relationship("Event", back_populates="odds")


__all__ = ["User", "NewsItem", "Fighter", "Event", "OddsRecord", "UserRole", "Base"]

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, default="UFC News")
    image_url = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
