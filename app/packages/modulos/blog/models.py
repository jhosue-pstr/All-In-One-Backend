import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Text, DateTime, Boolean, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel, TimestampMixin

class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"

class Category(BaseModel, TimestampMixin):
    __tablename__ = "blog_categories"

    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True
)

class Post(BaseModel, TimestampMixin):
    __tablename__ = "blog_posts"

    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id", ondelete="CASCADE"), nullable=False)

    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("blog_categories.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, default="")
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    featured_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[PostStatus] = mapped_column(
        SQLEnum(PostStatus),
        default=PostStatus.DRAFT,
        nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)