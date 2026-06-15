import anyio
from pathlib import Path
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.sitio import Sitio
from app.models.usuario import User

from app.packages.modulos.store.models import Carrito, ItemCarrito, Producto
from app.packages.modulos.store.schemas import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaResponse,
    ProductoCreate,
    ProductoUpdate,
    ProductoResponse,
    ProductoListado,
    PedidoListado,
    PedidoResponse,
    PedidoUpdateEstado,
    CarritoResponse,
    ItemCarritoCreate,
    ItemCarritoResponse,
    CheckoutRequest,
    CheckoutResponse,
)
from app.packages.modulos.store.services import StoreService


UPLOAD_DIR = Path("uploads/tienda")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SITIO_NO_ENCONTRADO = "Sitio no encontrado"
PRODUCTO_NO_ENCONTRADO = "Producto no encontrado"
CATEGORIA_NO_ENCONTRADA = "Categoría no encontrada"

router = APIRouter(prefix="/v1/sitios/{sitio_id}/tienda", tags=["tienda"])


def verificar_sitio(db: Session, sitio_id: int) -> None:
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=SITIO_NO_ENCONTRADO)


# ==================== PRODUCTOS ====================

@router.get(
    "/productos",
    response_model=dict,
    responses={404: {"description": "Sitio no encontrado"}}
)
def listar_productos(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)],
    categoria_id: Optional[int] = None,
    pagina: int = 1,
    por_pagina: int = 20,
    featured: bool = False,
):
    """
    Público: listar productos activos de la tienda.
    No muestra productos eliminados/inactivos.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    productos, total = service.listar_productos(
        categoria_id=categoria_id,
        solo_activos=True,
        featured=featured,
        page=pagina,
        per_page=por_pagina,
    )

    return {
        "success": True,
        "data": [ProductoListado.model_validate(p) for p in productos],
        "meta": {
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": (total + por_pagina - 1) // por_pagina,
        },
    }


@router.get(
    "/admin/productos",
    response_model=dict,
    responses={404: {"description": "Sitio no encontrado"}}
)
def listar_productos_admin(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.ver"))],
    categoria_id: Optional[int] = None,
    pagina: int = 1,
    por_pagina: int = 20,
    solo_activos: bool = True,
    featured: bool = False,
):
    """
    Administrativo: permite listar productos desde el panel.
    Puede incluir inactivos si solo_activos=False.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    productos, total = service.listar_productos(
        categoria_id=categoria_id,
        solo_activos=solo_activos,
        featured=featured,
        page=pagina,
        per_page=por_pagina,
    )

    return {
        "success": True,
        "data": [ProductoListado.model_validate(p) for p in productos],
        "meta": {
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": (total + por_pagina - 1) // por_pagina,
        },
    }


@router.post(
    "/productos",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Sitio no encontrado"}}
)
def crear_producto(
    sitio_id: int,
    producto_data: ProductoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.crear"))],
):
    """Administrativo: crear un nuevo producto."""
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    producto = service.crear_producto(
        producto_data,
        usuario_id=current_user.id,
    )

    return producto


@router.get(
    "/productos/{producto_id}",
    response_model=ProductoResponse,
    responses={404: {"description": "Producto o sitio no encontrado"}}
)
def obtener_producto(
    sitio_id: int,
    producto_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público: obtener un producto activo por ID.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    producto = service.get_producto(producto_id, solo_activos=True)

    if not producto:
        raise HTTPException(status_code=404, detail=PRODUCTO_NO_ENCONTRADO)

    return producto


@router.get(
    "/admin/productos/{producto_id}",
    response_model=ProductoResponse,
    responses={404: {"description": "Producto o sitio no encontrado"}}
)
def obtener_producto_admin(
    sitio_id: int,
    producto_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.ver"))],
):
    """
    Administrativo: obtener un producto aunque esté inactivo.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    producto = service.get_producto(producto_id, solo_activos=False)

    if not producto:
        raise HTTPException(status_code=404, detail=PRODUCTO_NO_ENCONTRADO)

    return producto


@router.put(
    "/productos/{producto_id}",
    response_model=ProductoResponse,
    responses={404: {"description": "Producto o sitio no encontrado"}}
)
def actualizar_producto(
    sitio_id: int,
    producto_id: int,
    producto_data: ProductoUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.editar"))],
):
    """Administrativo: actualizar un producto."""
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    producto = service.actualizar_producto(
        producto_id,
        producto_data,
        usuario_id=current_user.id,
    )

    if not producto:
        raise HTTPException(status_code=404, detail=PRODUCTO_NO_ENCONTRADO)

    return producto


@router.delete(
    "/productos/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Producto o sitio no encontrado"}}
)
def eliminar_producto(
    sitio_id: int,
    producto_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.eliminar"))],
):
    """
    Administrativo: eliminar producto.
    En el servicio debe hacerse soft delete: es_activo=False.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    eliminado = service.eliminar_producto(
        producto_id,
        usuario_id=current_user.id,
    )

    if not eliminado:
        raise HTTPException(status_code=404, detail=PRODUCTO_NO_ENCONTRADO)

    return None


# ==================== CATEGORÍAS ====================

@router.get(
    "/categorias",
    response_model=dict,
    responses={404: {"description": "Sitio no encontrado"}}
)
def listar_categorias(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público: listar categorías activas.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    categorias = service.listar_categorias(solo_activas=True)

    return {
        "success": True,
        "data": [CategoriaResponse.model_validate(c) for c in categorias],
    }


@router.get(
    "/admin/categorias",
    response_model=dict,
    responses={404: {"description": "Sitio no encontrado"}}
)
def listar_categorias_admin(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.ver"))],
    solo_activas: bool = True,
):
    """
    Administrativo: listar categorías.
    Puede incluir inactivas si solo_activas=False.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    categorias = service.listar_categorias(solo_activas=solo_activas)

    return {
        "success": True,
        "data": [CategoriaResponse.model_validate(c) for c in categorias],
    }


@router.post(
    "/categorias",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "Sitio no encontrado"}}
)
def crear_categoria(
    sitio_id: int,
    categoria_data: CategoriaCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.crear"))],
):
    """Administrativo: crear una nueva categoría."""
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    categoria = service.crear_categoria(
        categoria_data,
        usuario_id=current_user.id,
    )

    return categoria


@router.get(
    "/categorias/{categoria_id}",
    response_model=CategoriaResponse,
    responses={404: {"description": "Categoría o sitio no encontrado"}}
)
def obtener_categoria(
    sitio_id: int,
    categoria_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público: obtener una categoría activa por ID.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    categoria = service.get_categoria(categoria_id, solo_activas=True)

    if not categoria:
        raise HTTPException(status_code=404, detail=CATEGORIA_NO_ENCONTRADA)

    return categoria


@router.get(
    "/admin/categorias/{categoria_id}",
    response_model=CategoriaResponse,
    responses={404: {"description": "Categoría o sitio no encontrado"}}
)
def obtener_categoria_admin(
    sitio_id: int,
    categoria_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.ver"))],
):
    """
    Administrativo: obtener una categoría aunque esté inactiva.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    categoria = service.get_categoria(categoria_id, solo_activas=False)

    if not categoria:
        raise HTTPException(status_code=404, detail=CATEGORIA_NO_ENCONTRADA)

    return categoria


@router.put(
    "/categorias/{categoria_id}",
    response_model=CategoriaResponse,
    responses={404: {"description": "Categoría o sitio no encontrado"}}
)
def actualizar_categoria(
    sitio_id: int,
    categoria_id: int,
    categoria_data: CategoriaUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.editar"))],
):
    """Administrativo: actualizar una categoría."""
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    categoria = service.actualizar_categoria(
        categoria_id,
        categoria_data,
        usuario_id=current_user.id,
    )

    if not categoria:
        raise HTTPException(status_code=404, detail=CATEGORIA_NO_ENCONTRADA)

    return categoria


@router.delete(
    "/categorias/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Categoría o sitio no encontrado"}}
)
def eliminar_categoria(
    sitio_id: int,
    categoria_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.eliminar"))],
):
    """
    Administrativo: eliminar categoría.
    En el servicio debe hacerse soft delete: activa=False.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    eliminado = service.eliminar_categoria(
        categoria_id,
        usuario_id=current_user.id,
    )

    if not eliminado:
        raise HTTPException(status_code=404, detail=CATEGORIA_NO_ENCONTRADA)

    return None


# ==================== PEDIDOS ====================

@router.get(
    "/pedidos",
    response_model=dict,
    responses={404: {"description": "Sitio no encontrado"}}
)
def listar_pedidos(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.pedidos"))],
    estado: Optional[str] = None,
    pagina: int = 1,
    por_pagina: int = 20,
):
    """Administrativo: listar pedidos del sitio."""
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    pedidos, total = service.listar_pedidos(
        estado=estado,
        page=pagina,
        per_page=por_pagina,
    )

    return {
        "success": True,
        "data": [PedidoListado.model_validate(p) for p in pedidos],
        "meta": {
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": (total + por_pagina - 1) // por_pagina,
        },
    }


@router.get(
    "/pedidos/{pedido_id}",
    response_model=PedidoResponse,
    responses={404: {"description": "Pedido o sitio no encontrado"}}
)
def obtener_pedido(
    sitio_id: int,
    pedido_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.pedidos"))],
):
    """Administrativo: obtener un pedido por ID."""
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    pedido = service.get_pedido(pedido_id)

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    return pedido


@router.put(
    "/pedidos/{pedido_id}/estado",
    response_model=PedidoResponse,
    responses={
        400: {"description": "Error en la solicitud"},
        404: {"description": "Pedido o sitio no encontrado"},
    }
)
def actualizar_estado_pedido(
    sitio_id: int,
    pedido_id: int,
    data: PedidoUpdateEstado,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("tienda.pedidos"))],
):
    """Administrativo: actualizar el estado de un pedido."""
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)

    try:
        pedido = service.actualizar_estado_pedido(
            pedido_id,
            data.estado,
            usuario_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    return pedido


# ==================== CARRITO ====================

@router.get(
    "/carrito",
    response_model=CarritoResponse,
    responses={404: {"description": "Sitio no encontrado"}}
)
def obtener_carrito(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)],
    usuario_id: int = None,
):
    """
    Público/cliente del sitio: obtener el carrito actual.
    No usa roles internos del panel.
    """
    try:
        verificar_sitio(db, sitio_id)

        if not usuario_id:
            return CarritoResponse(id=0, site_id=sitio_id, items=[], total=0)

        result = db.execute(
            select(Carrito).where(
                Carrito.site_id == sitio_id,
                Carrito.usuario_id == usuario_id,
            )
        )
        carrito = result.scalar_one_or_none()

        if not carrito:
            return CarritoResponse(id=0, site_id=sitio_id, items=[], total=0)

        result = db.execute(
            select(ItemCarrito).where(ItemCarrito.carrito_id == carrito.id)
        )
        items = result.scalars().all()

        items_response = []
        total = 0

        for item in items:
            result = db.execute(
                select(Producto).where(
                    Producto.id == item.producto_id,
                    Producto.es_activo == True,
                )
            )
            producto = result.scalar_one_or_none()

            if producto:
                items_response.append(
                    ItemCarritoResponse(
                        id=item.id,
                        producto_id=item.producto_id,
                        cantidad=item.cantidad,
                        producto=ProductoListado.model_validate(producto),
                    )
                )
                total += producto.precio * item.cantidad

        return CarritoResponse(
            id=carrito.id,
            site_id=sitio_id,
            items=items_response,
            total=total,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en carrito: {e}")
        return CarritoResponse(id=0, site_id=sitio_id, items=[], total=0)


@router.post(
    "/carrito/items",
    responses={
        401: {"description": "Debes iniciar sesión para agregar al carrito"},
        400: {"description": "Error en la solicitud"},
        404: {"description": "Sitio no encontrado"},
        500: {"description": "Error interno"},
    }
)
def agregar_al_carrito(
    sitio_id: int,
    item_data: ItemCarritoCreate,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público/cliente del sitio: agregar un producto al carrito.
    No usa roles internos del panel.
    """
    try:
        verificar_sitio(db, sitio_id)

        usuario_id = (
            item_data.usuario_id
            if hasattr(item_data, "usuario_id") and item_data.usuario_id
            else None
        )

        if not usuario_id:
            raise HTTPException(
                status_code=401,
                detail="Debes iniciar sesión para agregar al carrito",
            )

        service = StoreService(db, sitio_id)

        try:
            item = service.agregar_al_carrito(
                producto_id=item_data.producto_id,
                cantidad=item_data.cantidad,
                usuario_id=usuario_id,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        db.refresh(item, ["producto"])

        return JSONResponse(
            content=jsonable_encoder(
                {
                    "id": item.id,
                    "producto_id": item.producto_id,
                    "cantidad": item.cantidad,
                    "producto": ProductoListado.model_validate(item.producto).model_dump(),
                }
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al agregar al carrito: {e}")
        raise HTTPException(status_code=500, detail="Error interno")


@router.put(
    "/carrito/items/{item_id}",
    response_model=ItemCarritoResponse,
    responses={404: {"description": "Item o sitio no encontrado"}}
)
def actualizar_cantidad_carrito(
    sitio_id: int,
    item_id: int,
    cantidad: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público/cliente del sitio: actualizar cantidad de item.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    item = service.actualizar_cantidad_carrito(item_id, cantidad)

    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    db.refresh(item, ["producto"])

    return ItemCarritoResponse(
        id=item.id,
        producto_id=item.producto_id,
        cantidad=item.cantidad,
        producto=ProductoListado.model_validate(item.producto),
    )


@router.delete(
    "/carrito/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Item o sitio no encontrado"}}
)
def eliminar_del_carrito(
    sitio_id: int,
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público/cliente del sitio: eliminar item del carrito.
    """
    verificar_sitio(db, sitio_id)

    service = StoreService(db, sitio_id)
    eliminado = service.eliminar_del_carrito(item_id)

    if not eliminado:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    return None


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    responses={
        400: {"description": "Debes iniciar sesión o error en la solicitud"},
        404: {"description": "Sitio no encontrado"},
        500: {"description": "Error interno al procesar el pedido"},
    }
)
def realizar_checkout(
    sitio_id: int,
    checkout_data: CheckoutRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Público/cliente del sitio: procesar checkout.
    Crear pedido puede quedar público porque lo hace el comprador.
    """
    verificar_sitio(db, sitio_id)

    usuario_id = (
        checkout_data.usuario_id
        if hasattr(checkout_data, "usuario_id") and checkout_data.usuario_id
        else None
    )

    if not usuario_id:
        raise HTTPException(
            status_code=400,
            detail="Debes iniciar sesión para finalizar la compra",
        )

    service = StoreService(db, sitio_id)

    try:
        pedido = service.crear_pedido(
            checkout_data,
            usuario_id=usuario_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error en checkout: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el pedido: {str(e)}",
        )

    return CheckoutResponse(
        pedido=PedidoResponse.model_validate(pedido),
        mensaje="Pedido creado exitosamente",
    )


# ==================== IMÁGENES ====================

@router.post(
    "/upload-image",
    responses={
        400: {"description": "Error en la solicitud (tipo/archivo inválido)"},
        500: {"description": "Error interno al guardar la imagen"},
    }
)
async def upload_tienda_image(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[User, Depends(require_permission("tienda.crear"))],
):
    """
    Administrativo: subir imagen para productos de tienda.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    allowed_extensions = {"jpg", "jpeg", "png", "webp", "gif"}

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
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    try:
        async with await anyio.open_file(file_path, "wb") as buffer:
            await buffer.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"url": f"/uploads/tienda/{filename}"}