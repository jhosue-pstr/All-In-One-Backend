from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session # <-- Cambiado
from sqlalchemy import select
from typing import List
import shutil
import uuid
from pathlib import Path

from app.db.database import get_db
from app.packages.modulos.blog import schemas, services
from app.packages.modulos.blog.models import Post, Category, PostStatus

router = APIRouter(prefix="/modules/blog", tags=["Module: Blog"])

@router.post("/{site_id}/categories", response_model=schemas.CategoryResponse)
def create_category_route(
    site_id: int,
    category_in: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    return services.create_category(db, site_id, category_in)

@router.post("/{site_id}/posts", response_model=schemas.PostResponse)
def create_post_route(
    site_id: int,
    post_in: schemas.PostCreate,
    db: Session = Depends(get_db)
):
    return services.create_post(db, site_id, post_in)


@router.get("/{site_id}/posts", response_model=List[schemas.PostResponse])
def list_posts_route(
    site_id: int,
    only_published: bool = False,
    db: Session = Depends(get_db)
):
    return services.get_posts_by_site(db, site_id, only_published)


@router.get("/{site_id}/posts/{slug}", response_model=schemas.PostResponse)
def get_post_route(
    site_id: int,
    slug: str,
    db: Session = Depends(get_db)
):
    return services.get_post_by_slug(db, site_id, slug)


@router.put("/{site_id}/posts/{post_id}", response_model=schemas.PostResponse)
def update_post_route(
    site_id: int,
    post_id: int,
    post_in: schemas.PostUpdate,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(Post).where(Post.id == post_id, Post.site_id == site_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    update_data = post_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


@router.delete("/{site_id}/posts/{post_id}")
def delete_post_route(
    site_id: int,
    post_id: int,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(Post).where(Post.id == post_id, Post.site_id == site_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    db.delete(post)
    db.commit()
    return {"message": "Artículo eliminado correctamente"}


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

@router.post("/{site_id}/upload-image")
def upload_blog_image(site_id: int, file: UploadFile = File(...)):
    try:
        upload_path = Path("uploads/blog")
        upload_path.mkdir(parents=True, exist_ok=True)

        ext = Path(file.filename).suffix.lower().replace(".", "")

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Tipo de archivo no permitido"
            )

        new_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = upload_path / new_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"url": f"/uploads/blog/{new_filename}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error guardando imagen: {str(e)}"
        )