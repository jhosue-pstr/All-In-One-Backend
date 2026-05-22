from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import shutil
import uuid
from pathlib import Path

# Importamos tu configuracion de base de datos
from app.db.database import get_db
# Importamos nuestros schemas, servicios y modelos del blog
from packages.modulos.blog import schemas, services
from packages.modulos.blog.models import Post, Category, PostStatus

router = APIRouter(prefix="/modules/blog", tags=["Module: Blog"])

# ==========================================
# RUTAS PARA CATEGORÍAS
# ==========================================
@router.post("/{site_id}/categories", response_model=schemas.CategoryResponse)
async def create_category_route(
    site_id: int,
    category_in: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    return await services.create_category(db, site_id, category_in)

# ==========================================
# RUTAS PARA ARTÍCULOS (POSTS)
# ==========================================

@router.post("/{site_id}/posts", response_model=schemas.PostResponse)
async def create_post_route(
    site_id: int,
    post_in: schemas.PostCreate,
    db: AsyncSession = Depends(get_db)
):
    return await services.create_post(db, site_id, post_in)


@router.get("/{site_id}/posts", response_model=List[schemas.PostResponse])
async def list_posts_route(
    site_id: int,
    only_published: bool = False,
    db: AsyncSession = Depends(get_db)
):
    return await services.get_posts_by_site(db, site_id, only_published)


@router.get("/{site_id}/posts/{slug}", response_model=schemas.PostResponse)
async def get_post_route(
    site_id: int,
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    return await services.get_post_by_slug(db, site_id, slug)


@router.put("/{site_id}/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post_route(
    site_id: int,
    post_id: int,
    post_in: schemas.PostUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.site_id == site_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    update_data = post_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{site_id}/posts/{post_id}")
async def delete_post_route(
    site_id: int,
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.site_id == site_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    await db.delete(post)
    await db.commit()
    return {"message": "Artículo eliminado correctamente"}


# ==========================================
# 📸 UPLOAD SEGURO (FIX SONAR S2083)
# ==========================================

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


@router.post("/{site_id}/upload-image")
async def upload_blog_image(site_id: int, file: UploadFile = File(...)):
    try:
        # 📁 carpeta segura
        upload_path = Path("/app/uploads/blog")
        upload_path.mkdir(parents=True, exist_ok=True)

        # 🔒 obtener extensión segura
        ext = Path(file.filename).suffix.lower().replace(".", "")

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no permitido"
            )

        # 🔥 nombre seguro
        new_filename = f"{uuid.uuid4().hex}.{ext}"

        # 🛡️ path seguro (NO string concatenation)
        file_path = upload_path / new_filename

        # 💾 guardar archivo
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"url": f"/uploads/blog/{new_filename}"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error guardando imagen: {str(e)}"
        )