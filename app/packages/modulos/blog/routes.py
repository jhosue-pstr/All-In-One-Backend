import anyio
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, List
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.usuario import User
from app.packages.modulos.blog import schemas, services
from app.packages.modulos.blog.models import Post

UPLOAD_DIR = Path("uploads/blog")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ARTICULO_NO_ENCONTRADO = "Artículo no encontrado"
ARTICULO_NO_DISPONIBLE = "Artículo no disponible"

router = APIRouter(prefix="/modules/blog", tags=["Module: Blog"])


def is_post_publicly_available(post: Post) -> bool:
    """
    Un post es visible públicamente si:
    - está publicado
    - o está programado y su fecha ya llegó
    """
    now = datetime.now(timezone.utc)

    if post.status == "published":
        return True

    if post.status == "scheduled" and post.published_at is not None:
        return post.published_at <= now

    return False


@router.post("/{site_id}/categories", response_model=schemas.CategoryResponse)
def create_category_route(
    site_id: int,
    category_in: schemas.CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return services.create_category(db, site_id, category_in)


@router.post("/{site_id}/posts", response_model=schemas.PostResponse)
def create_post_route(
    site_id: int,
    post_in: schemas.PostCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return services.create_post(db, site_id, post_in)


@router.get("/{site_id}/posts", response_model=List[schemas.PostResponse])
def list_posts_route(
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    only_published: bool = False,
):
    if not only_published:
        return services.get_posts_by_site(db, site_id, only_published=False)

    now = datetime.now(timezone.utc)

    result = db.execute(
        select(Post)
        .where(
            Post.site_id == site_id,
            or_(
                Post.status == "published",
                and_(
                    Post.status == "scheduled",
                    Post.published_at.is_not(None),
                    Post.published_at <= now,
                ),
            ),
        )
        .order_by(Post.published_at.desc().nullslast(), Post.created_at.desc())
    )

    return result.scalars().all()


@router.get(
    "/{site_id}/posts/{slug}",
    response_model=schemas.PostResponse,
    responses={
        404: {"description": "Artículo no encontrado o no disponible"}
    }
)
def get_post_route(
    site_id: int,
    slug: str,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Este endpoint lo usa el sitio publicado para ver el detalle del post.
    Por eso bloqueamos borradores, archivados y programados futuros.
    """
    result = db.execute(
        select(Post).where(
            Post.site_id == site_id,
            Post.slug == slug,
        )
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail=ARTICULO_NO_ENCONTRADO)

    if not is_post_publicly_available(post):
        raise HTTPException(status_code=404, detail=ARTICULO_NO_DISPONIBLE)

    return post


@router.put(
    "/{site_id}/posts/{post_id}",
    response_model=schemas.PostResponse,
    responses={
        404: {"description": "Artículo no encontrado"}
    }
)
def update_post_route(
    site_id: int,
    post_id: int,
    post_in: schemas.PostUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(Post).where(
            Post.id == post_id,
            Post.site_id == site_id,
        )
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail=ARTICULO_NO_ENCONTRADO)

    update_data = post_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    return post


@router.delete(
    "/{site_id}/posts/{post_id}",
    responses={
        404: {"description": "Artículo no encontrado"}
    }
)
def delete_post_route(
    site_id: int,
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(Post).where(
            Post.id == post_id,
            Post.site_id == site_id,
        )
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail=ARTICULO_NO_ENCONTRADO)

    db.delete(post)
    db.commit()

    return {"message": "Artículo eliminado correctamente"}


@router.post(
    "/{site_id}/upload-image",
    responses={
        400: {"description": "Error en la solicitud (tipo/archivo inválido)"},
        500: {"description": "Error interno al guardar la imagen"}
    }
)
async def upload_blog_image(
    site_id: int,
    file: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Guarda la imagen físicamente en:
        uploads/blog/

    Y devuelve una URL para guardar en DB:
        /uploads/blog/nombre_archivo.ext
    """

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    allowed_extensions = {
        "jpg",
        "jpeg",
        "png",
        "webp",
        "gif",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes JPG, PNG, WEBP o GIF",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo no tiene nombre válido",
        )

    extension = Path(file.filename).suffix.lower().replace(".", "")

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Extensión de imagen no permitida",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío",
        )

    try:
        async with await anyio.open_file(file_path, "wb") as buffer:
            await buffer.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "url": f"/uploads/blog/{filename}",
    }