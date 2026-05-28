from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from app.db.database import get_db
from app.models.sitio import Sitio

# --- MÓDULO STORE ---
from app.packages.modulos.store.models import Carrito, ItemCarrito, Producto
from app.packages.modulos.store.schemas import (
    CategoriaCreate, CategoriaUpdate, CategoriaResponse,
    ProductoCreate, ProductoUpdate, ProductoResponse, ProductoListado,
    PedidoListado, PedidoResponse, PedidoUpdateEstado,
    CarritoResponse, ItemCarritoCreate, ItemCarritoResponse,
    CheckoutRequest, CheckoutResponse
)
from app.packages.modulos.store.services import StoreService


UPLOAD_DIR = Path("uploads/tienda")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/v1/sitios/{sitio_id}/tienda", tags=["tienda"])

# ==================== PRODUCTOS ====================

@router.get("/productos", response_model=dict)
def listar_productos(
    sitio_id: int,
    categoria_id: Optional[int] = None,
    pagina: int = 1,
    por_pagina: int = 20,
    solo_activos: bool = True,
    featured: bool = False,
    db: Session = Depends(get_db)
):
    """Listar productos de la tienda"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    productos, total = service.listar_productos(
        categoria_id=categoria_id,
        solo_activos=solo_activos,
        featured=featured,
        page=pagina,
        per_page=por_pagina
    )
    
    return {
        "success": True,
        "data": [ProductoListado.model_validate(p) for p in productos],
        "meta": {
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": (total + por_pagina - 1) // por_pagina
        }
    }


@router.post("/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(
    sitio_id: int,
    producto_data: ProductoCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    producto = service.crear_producto(producto_data)
    return producto


@router.get("/productos/{producto_id}", response_model=ProductoResponse)
def obtener_producto(
    sitio_id: int,
    producto_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un producto por ID"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    producto = service.get_producto(producto_id)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto


@router.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    sitio_id: int,
    producto_id: int,
    producto_data: ProductoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un producto"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    producto = service.actualizar_producto(producto_id, producto_data)
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto


@router.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    sitio_id: int,
    producto_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un producto"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    eliminado = service.eliminar_producto(producto_id)
    
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return None


# ==================== CATEGORÍAS ====================

@router.get("/categorias", response_model=dict)
def listar_categorias(
    sitio_id: int,
    solo_activas: bool = True,
    db: Session = Depends(get_db)
):
    """Listar categorías de productos"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    categorias = service.listar_categorias(solo_activas=solo_activas)
    
    return {
        "success": True,
        "data": [CategoriaResponse.model_validate(c) for c in categorias]
    }


@router.post("/categorias", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    sitio_id: int,
    categoria_data: CategoriaCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva categoría"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    categoria = service.crear_categoria(categoria_data)
    return categoria


@router.get("/categorias/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(
    sitio_id: int,
    categoria_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una categoría por ID"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    categoria = service.get_categoria(categoria_id)
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return categoria


@router.put("/categorias/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(
    sitio_id: int,
    categoria_id: int,
    categoria_data: CategoriaUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una categoría"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    categoria = service.actualizar_categoria(categoria_id, categoria_data)
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return categoria


@router.delete("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    sitio_id: int,
    categoria_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una categoría"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    eliminado = service.eliminar_categoria(categoria_id)
    
    if not eliminado:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return None


# ==================== PEDIDOS ====================

@router.get("/pedidos", response_model=dict)
def listar_pedidos(
    sitio_id: int,
    estado: Optional[str] = None,
    pagina: int = 1,
    por_pagina: int = 20,
    db: Session = Depends(get_db)
):
    """Listar pedidos del sitio"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    pedidos, total = service.listar_pedidos(
        estado=estado,
        page=pagina,
        per_page=por_pagina
    )
    
    return {
        "success": True,
        "data": [PedidoListado.model_validate(p) for p in pedidos],
        "meta": {
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": (total + por_pagina - 1) // por_pagina
        }
    }


@router.get("/pedidos/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(
    sitio_id: int,
    pedido_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un pedido por ID"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    pedido = service.get_pedido(pedido_id)
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    return pedido


@router.put("/pedidos/{pedido_id}/estado", response_model=PedidoResponse)
def actualizar_estado_pedido(
    sitio_id: int,
    pedido_id: int,
    data: PedidoUpdateEstado,
    db: Session = Depends(get_db)
):
    """Actualizar el estado de un pedido"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    
    try:
        pedido = service.actualizar_estado_pedido(pedido_id, data.estado)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    return pedido


# ==================== CARRITO ====================

@router.get("/carrito", response_model=CarritoResponse)
def obtener_carrito(
    sitio_id: int,
    usuario_id: int = None,
    db: Session = Depends(get_db)
):
    """Obtener el carrito actual (por usuario_id)"""
    try:
        result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Sitio no encontrado")
        
        if not usuario_id:
            return CarritoResponse(id=0, site_id=sitio_id, items=[], total=0)
        
        result = db.execute(
            select(Carrito).where(
                Carrito.site_id == sitio_id,
                Carrito.usuario_id == usuario_id
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
                select(Producto).where(Producto.id == item.producto_id, Producto.es_activo == True)
            )
            producto = result.scalar_one_or_none()
            
            if producto:
                items_response.append(ItemCarritoResponse(
                    id=item.id,
                    producto_id=item.producto_id,
                    cantidad=item.cantidad,
                    producto=ProductoListado.model_validate(producto)
                ))
                total += producto.precio * item.cantidad
        
        return CarritoResponse(
            id=carrito.id,
            site_id=sitio_id,
            items=items_response,
            total=total
        )
    except Exception as e:
        print(f"Error en carrito: {e}")
        return CarritoResponse(id=0, site_id=sitio_id, items=[], total=0)


@router.post("/carrito/items")
def agregar_al_carrito(
    sitio_id: int,
    item_data: ItemCarritoCreate,
    db: Session = Depends(get_db)
):
    """Agregar un producto al carrito"""
    from fastapi.responses import JSONResponse
    from fastapi.encoders import jsonable_encoder
    try:
        result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Sitio no encontrado")
        
        usuario_id = item_data.usuario_id if hasattr(item_data, 'usuario_id') and item_data.usuario_id else None
        
        if not usuario_id:
            raise HTTPException(status_code=401, detail="Debes iniciar sesión para agregar al carrito")
        
        service = StoreService(db, sitio_id)
        
        try:
            item = service.agregar_al_carrito(
                producto_id=item_data.producto_id,
                cantidad=item_data.cantidad,
                usuario_id=usuario_id
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        db.refresh(item, ["producto"])
        
        return JSONResponse(content=jsonable_encoder({
            "id": item.id,
            "producto_id": item.producto_id,
            "cantidad": item.cantidad,
            "producto": ProductoListado.model_validate(item.producto).model_dump(),
        }))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al agregar al carrito: {e}")
        raise HTTPException(status_code=500, detail="Error interno")


@router.put("/carrito/items/{item_id}", response_model=ItemCarritoResponse)
def actualizar_cantidad_carrito(
    sitio_id: int,
    item_id: int,
    cantidad: int,
    db: Session = Depends(get_db)
):
    """Actualizar la cantidad de un item en el carrito"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    item = service.actualizar_cantidad_carrito(item_id, cantidad)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    db.refresh(item, ["producto"])
    
    return ItemCarritoResponse(
        id=item.id,
        producto_id=item.producto_id,
        cantidad=item.cantidad,
        producto=ProductoListado.model_validate(item.producto)
    )


@router.delete("/carrito/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_del_carrito(
    sitio_id: int,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un item del carrito"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    service = StoreService(db, sitio_id)
    eliminado = service.eliminar_del_carrito(item_id)
    
    if not eliminado:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    return None


@router.post("/checkout", response_model=CheckoutResponse)
def realizar_checkout(
    sitio_id: int,
    checkout_data: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Procesar el checkout y crear un pedido"""
    result = db.execute(select(Sitio).where(Sitio.id == sitio_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    usuario_id = checkout_data.usuario_id if hasattr(checkout_data, 'usuario_id') and checkout_data.usuario_id else None
    
    if not usuario_id:
        raise HTTPException(status_code=400, detail="Debes iniciar sesión para finalizar la compra")
    
    service = StoreService(db, sitio_id)
    
    try:
        pedido = service.crear_pedido(checkout_data, usuario_id=usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error en checkout: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar el pedido: {str(e)}")
    
    return CheckoutResponse(
        pedido=PedidoResponse.model_validate(pedido),
        mensaje="Pedido creado exitosamente"
    )


@router.post("/upload-image")
async def upload_tienda_image(
    file: UploadFile = File(...),
):
    """Subir imagen para productos de tienda"""
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    allowed_extensions = {"jpg", "jpeg", "png", "webp", "gif"}

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes JPG, PNG, WEBP o GIF")

    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre válido")

    extension = Path(file.filename).suffix.lower().replace(".", "")

    if extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Extensión de imagen no permitida")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"url": f"/uploads/tienda/{filename}"}