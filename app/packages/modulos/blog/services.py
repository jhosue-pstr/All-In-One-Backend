import re
import unicodedata
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.packages.modulos.analitica.services import registrar_evento
from app.packages.modulos.analitica.schemas import EventoCreate
from app.packages.modulos.blog.models import Category, Post, PostStatus
from app.packages.modulos.blog.schemas import CategoryCreate, PostCreate, PostUpdate

ARTICULO_NO_ENCONTRADO = "Artículo no encontrado"
CATEGORIA_NO_ENCONTRADA = "Categoría no encontrada"


def generate_slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug


def _snapshot(obj) -> dict:
    return jsonable_encoder(obj)


def _registrar_auditoria(
    db: Session,
    *,
    entidad: str,
    entidad_id: int,
    accion: str,
    usuario_id: Optional[int] = None,
    valores_anteriores: Optional[dict] = None,
    valores_nuevos: Optional[dict] = None,
) -> None:
    auditoria = Auditoria(
        entidad=entidad,
        entidad_id=entidad_id,
        accion=accion,
        usuario_id=usuario_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=valores_nuevos,
    )
    db.add(auditoria)


def generate_unique_post_slug(db: Session, site_id: int, title: str) -> str:
    base_slug = generate_slug(title)
    slug = base_slug
    counter = 1

    while True:
        result = db.execute(
            select(Post).where(
                Post.site_id == site_id,
                Post.slug == slug,
                Post.is_deleted.is_(False),
            )
        )
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def generate_unique_category_slug(db: Session, site_id: int, name: str) -> str:
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 1

    while True:
        result = db.execute(
            select(Category).where(
                Category.site_id == site_id,
                Category.slug == slug,
                Category.is_deleted.is_(False),
            )
        )
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


# --- SERVICIOS DE POSTS ---

def create_post(db: Session, site_id: int, post_in: PostCreate, usuario_id: Optional[int] = None) -> Post:
    unique_slug = generate_unique_post_slug(db, site_id, post_in.title)

    new_post = Post(
        site_id=site_id,
        slug=unique_slug,
        **post_in.model_dump()
    )
    db.add(new_post)
    db.flush()

    _registrar_auditoria(
        db,
        entidad="blog_posts",
        entidad_id=new_post.id,
        accion="INSERT",
        usuario_id=usuario_id,
        valores_nuevos=_snapshot(new_post),
    )

    registrar_evento(
        db, site_id,
        EventoCreate(tipo="blog.post_created", etiqueta=new_post.title, url=f"/blog/{new_post.slug}"),
    )

    db.commit()
    db.refresh(new_post)
    return new_post


def get_posts_by_site(db: Session, site_id: int, only_published: bool = False):
    query = select(Post).where(
        Post.site_id == site_id,
        Post.is_deleted.is_(False),
    )

    if only_published:
        now = datetime.now(timezone.utc)
        query = query.where(
            or_(
                Post.status == PostStatus.PUBLISHED,
                and_(
                    Post.status == PostStatus.SCHEDULED,
                    Post.published_at.isnot(None),
                    Post.published_at <= now,
                ),
            )
        )

    result = db.execute(query.order_by(Post.published_at.desc().nullslast(), Post.created_at.desc()))
    return result.scalars().all()


def get_post_by_slug(db: Session, site_id: int, slug: str) -> Post:
    result = db.execute(
        select(Post).where(
            Post.site_id == site_id,
            Post.slug == slug,
            Post.is_deleted.is_(False),
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail=ARTICULO_NO_ENCONTRADO)
    return post


def get_post_by_id(db: Session, site_id: int, post_id: int) -> Post:
    result = db.execute(
        select(Post).where(
            Post.id == post_id,
            Post.site_id == site_id,
            Post.is_deleted.is_(False),
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail=ARTICULO_NO_ENCONTRADO)
    return post


def update_post(
    db: Session,
    site_id: int,
    post_id: int,
    post_in: PostUpdate,
    usuario_id: Optional[int] = None,
) -> Post:
    post = get_post_by_id(db, site_id, post_id)
    valores_anteriores = _snapshot(post)
    update_data = post_in.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"] and update_data["title"] != post.title:
        update_data["slug"] = generate_unique_post_slug(db, site_id, update_data["title"])

    for field, value in update_data.items():
        setattr(post, field, value)

    db.flush()

    _registrar_auditoria(
        db,
        entidad="blog_posts",
        entidad_id=post.id,
        accion="UPDATE",
        usuario_id=usuario_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=_snapshot(post),
    )

    if update_data.get("status") == "published" and post.status != PostStatus.PUBLISHED:
        registrar_evento(
            db, site_id,
            EventoCreate(tipo="blog.post_published", etiqueta=post.title, url=f"/blog/{post.slug}"),
        )

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, site_id: int, post_id: int, usuario_id: Optional[int] = None) -> None:
    post = get_post_by_id(db, site_id, post_id)
    valores_anteriores = _snapshot(post)

    post.is_deleted = True
    post.deleted_at = datetime.now(timezone.utc)
    post.deleted_by = usuario_id

    db.flush()

    _registrar_auditoria(
        db,
        entidad="blog_posts",
        entidad_id=post.id,
        accion="DELETE",
        usuario_id=usuario_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=_snapshot(post),
    )

    db.commit()


# --- SERVICIOS DE CATEGORÍAS ---

def create_category(
    db: Session,
    site_id: int,
    cat_in: CategoryCreate,
    usuario_id: Optional[int] = None,
) -> Category:
    slug = generate_unique_category_slug(db, site_id, cat_in.name)

    new_cat = Category(
        site_id=site_id,
        slug=slug,
        **cat_in.model_dump()
    )
    db.add(new_cat)
    db.flush()

    _registrar_auditoria(
        db,
        entidad="blog_categories",
        entidad_id=new_cat.id,
        accion="INSERT",
        usuario_id=usuario_id,
        valores_nuevos=_snapshot(new_cat),
    )

    db.commit()
    db.refresh(new_cat)
    return new_cat


def get_categories_by_site(db: Session, site_id: int):
    result = db.execute(
        select(Category)
        .where(
            Category.site_id == site_id,
            Category.is_deleted.is_(False),
        )
        .order_by(Category.name.asc())
    )
    return result.scalars().all()


def get_category_by_id(db: Session, site_id: int, category_id: int) -> Category:
    result = db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.site_id == site_id,
            Category.is_deleted.is_(False),
        )
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail=CATEGORIA_NO_ENCONTRADA)
    return category


def update_category(
    db: Session,
    site_id: int,
    category_id: int,
    cat_in: CategoryCreate,
    usuario_id: Optional[int] = None,
) -> Category:
    category = get_category_by_id(db, site_id, category_id)
    valores_anteriores = _snapshot(category)
    update_data = cat_in.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] and update_data["name"] != category.name:
        update_data["slug"] = generate_unique_category_slug(db, site_id, update_data["name"])

    for field, value in update_data.items():
        setattr(category, field, value)

    db.flush()

    _registrar_auditoria(
        db,
        entidad="blog_categories",
        entidad_id=category.id,
        accion="UPDATE",
        usuario_id=usuario_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=_snapshot(category),
    )

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, site_id: int, category_id: int, usuario_id: Optional[int] = None) -> None:
    category = get_category_by_id(db, site_id, category_id)
    valores_anteriores = _snapshot(category)

    category.is_deleted = True
    category.deleted_at = datetime.now(timezone.utc)
    category.deleted_by = usuario_id

    db.flush()

    _registrar_auditoria(
        db,
        entidad="blog_categories",
        entidad_id=category.id,
        accion="DELETE",
        usuario_id=usuario_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=_snapshot(category),
    )

    db.commit()
