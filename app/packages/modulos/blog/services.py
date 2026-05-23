import re
import unicodedata
from sqlalchemy.orm import Session  # <-- Cambiado a Session síncrona
from sqlalchemy import select, or_, and_
from fastapi import HTTPException
from datetime import datetime, timezone

from app.packages.modulos.blog.models import Post, Category, PostStatus
from app.packages.modulos.blog.schemas import PostCreate, CategoryCreate, PostUpdate

def generate_slug(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug

def generate_unique_post_slug(db: Session, site_id: int, title: str) -> str:
    base_slug = generate_slug(title)
    slug = base_slug
    counter = 1
    
    while True:
        result = db.execute(select(Post).where(Post.site_id == site_id, Post.slug == slug))
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1

# --- SERVICIOS DE POSTS ---

def create_post(db: Session, site_id: int, post_in: PostCreate) -> Post:
    unique_slug = generate_unique_post_slug(db, site_id, post_in.title)
    
    new_post = Post(
        site_id=site_id,
        slug=unique_slug,
        **post_in.model_dump()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def get_posts_by_site(db: Session, site_id: int, only_published: bool = False):
    query = select(Post).where(Post.site_id == site_id)
    
    if only_published:
        now = datetime.now(timezone.utc)
        query = query.where(
            or_(
                Post.status == PostStatus.PUBLISHED,
                and_(
                    Post.status == PostStatus.SCHEDULED,
                    Post.published_at.isnot(None), 
                    Post.published_at <= now
                )
            )
        )
        
    result = db.execute(query.order_by(Post.created_at.desc()))
    return result.scalars().all()

def get_post_by_slug(db: Session, site_id: int, slug: str) -> Post:
    result = db.execute(select(Post).where(Post.site_id == site_id, Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return post

# --- SERVICIOS DE CATEGORÍAS ---

def create_category(db: Session, site_id: int, cat_in: CategoryCreate) -> Category:
    slug = generate_slug(cat_in.name) 
    
    new_cat = Category(
        site_id=site_id,
        slug=slug,
        **cat_in.model_dump()
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat