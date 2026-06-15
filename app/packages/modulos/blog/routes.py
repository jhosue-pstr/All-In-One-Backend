import anyio
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, List
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.permissions import require_permission
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
    - no está eliminado lógicamente
    - está publicado
    - o está programado y su fecha ya llegó
    """
    if post.is_deleted:
        return False

    now = datetime.now(timezone.utc)

    if post.status == "published":
        return True

    if post.status == "scheduled" and post.published_at is not None:
        return post.published_at <= now

    return False


# ==========================
# CATEGORÍAS
# ==========================

@router.post("/{site_id}/categories", response_model=schemas.CategoryResponse)
def create_category_route(
    site_id: int,
    category_in: schemas.CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("blog.crear"))],
):
    return services.create_category(
        db,
        site_id,
        category_in,
        usuario_id=current_user.id,
    )


@router.get("/{site_id}/categories", response_model=List[schemas.CategoryResponse])
def list_categories_route(
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público: permite que el sitio publicado pueda cargar categorías del blog.
    """
    return services.get_categories_by_site(db, site_id)


@router.put("/{site_id}/categories/{category_id}", response_model=schemas.CategoryResponse)
def update_category_route(
    site_id: int,
    category_id: int,
    category_in: schemas.CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("blog.editar"))],
):
    return services.update_category(
        db,
        site_id,
        category_id,
        category_in,
        usuario_id=current_user.id,
    )


@router.delete(
    "/{site_id}/categories/{category_id}",
    responses={
        404: {"description": "Categoría no encontrada"}
    }
)
def delete_category_route(
    site_id: int,
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("blog.eliminar"))],
):
    services.delete_category(
        db,
        site_id,
        category_id,
        usuario_id=current_user.id,
    )

    return {"message": "Categoría eliminada correctamente"}


# ==========================
# POSTS
# ==========================

@router.post("/{site_id}/posts", response_model=schemas.PostResponse)
def create_post_route(
    site_id: int,
    post_in: schemas.PostCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("blog.crear"))],
):
    return services.create_post(
        db,
        site_id,
        post_in,
        usuario_id=current_user.id,
    )


@router.get("/{site_id}/posts", response_model=List[schemas.PostResponse])
def list_posts_route(
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    only_published: bool = True,
):
    """
    Público: este endpoint lo usa el widget/sitio publicado.
    Por seguridad, siempre debe usarse para publicaciones visibles.
    """
    if not only_published:
        raise HTTPException(
            status_code=403,
            detail="Para ver borradores o publicaciones no públicas usa el endpoint administrativo.",
        )

    return services.get_posts_by_site(
        db,
        site_id,
        only_published=True,
    )


@router.get("/{site_id}/admin/posts", response_model=List[schemas.PostResponse])
def list_admin_posts_route(
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("blog.ver"))],
):
    """
    Administrativo: permite ver posts publicados, borradores, programados y archivados,
    excepto los eliminados lógicamente.
    """
    return services.get_posts_by_site(
        db,
        site_id,
        only_published=False,
    )


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
    Público: detalle del post publicado.
    Bloquea borradores, archivados, eliminados y programados futuros.
    """
    post = services.get_post_by_slug(db, site_id, slug)

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
    current_user: Annotated[User, Depends(require_permission("blog.editar"))],
):
    return services.update_post(
        db,
        site_id,
        post_id,
        post_in,
        usuario_id=current_user.id,
    )


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
    current_user: Annotated[User, Depends(require_permission("blog.eliminar"))],
):
    services.delete_post(
        db,
        site_id,
        post_id,
        usuario_id=current_user.id,
    )

    return {"message": "Artículo eliminado correctamente"}


# ==========================
# IMÁGENES DEL BLOG
# ==========================

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
    current_user: Annotated[User, Depends(require_permission("blog.crear"))],
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