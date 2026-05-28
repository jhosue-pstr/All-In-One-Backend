from datetime import datetime
from decimal import Decimal
import uuid
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import select, func, delete
from app.packages.modulos.store.models import (
    Categoria, Producto, Pedido, ItemPedido, Carrito, ItemCarrito,
    PedidoEstado, PedidoEstadoPago
)
from app.packages.modulos.store.schemas import (
    CategoriaCreate, CategoriaUpdate, ProductoCreate, ProductoUpdate,
    CheckoutRequest
)

class StoreService:
    def __init__(self, db: Session, sitio_id: int):
        self.db = db
        self.sitio_id = sitio_id
    
    def crear_categoria(self, data: CategoriaCreate) -> Categoria:
        categoria = Categoria(
            site_id=self.sitio_id, # Nota: el modelo actual en BD usa site_id, se respeta para que coincida
            **data.model_dump()
        )
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def get_categoria(self, categoria_id: int) -> Categoria | None:
        result = self.db.execute(
            select(Categoria).where(
                Categoria.id == categoria_id,
                Categoria.site_id == self.sitio_id
            )
        )
        return result.scalar_one_or_none()

    def listar_categorias(self, solo_activas: bool = True) -> list[Categoria]:
        query = select(Categoria).where(Categoria.site_id == self.sitio_id)
        if solo_activas:
            query = query.where(Categoria.activa == True)
        query = query.order_by(Categoria.orden, Categoria.nombre)
        result = self.db.execute(query)
        return list(result.scalars().all())

    def actualizar_categoria(self, categoria_id: int, data: CategoriaUpdate) -> Categoria | None:
        categoria = self.get_categoria(categoria_id)
        if not categoria:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(categoria, key, value)
        
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def eliminar_categoria(self, categoria_id: int) -> bool:
        categoria = self.get_categoria(categoria_id)
        if not categoria:
            return False
        self.db.delete(categoria)
        self.db.commit()
        return True

    # ==================== PRODUCTOS ====================

    def crear_producto(self, data: ProductoCreate) -> Producto:
        producto = Producto(
            site_id=self.sitio_id,
            **data.model_dump()
        )
        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def get_producto(self, producto_id: int) -> Producto | None:
        result = self.db.execute(
            select(Producto).where(
                Producto.id == producto_id,
                Producto.site_id == self.sitio_id
            )
        )
        return result.scalar_one_or_none()

    def listar_productos(
        self, 
        categoria_id: int | None = None,
        solo_activos: bool = True,
        featured: bool = False,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[list[Producto], int]:
        query = select(Producto).where(Producto.site_id == self.sitio_id)
        
        if solo_activos:
            query = query.where(Producto.es_activo == True)
        if categoria_id:
            query = query.where(Producto.categoria_id == categoria_id)
        if featured:
            query = query.where(Producto.es_featured == True)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Producto.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = self.db.execute(query)
        return list(result.scalars().all()), total

    def actualizar_producto(self, producto_id: int, data: ProductoUpdate) -> Producto | None:
        producto = self.get_producto(producto_id)
        if not producto:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(producto, key, value)
        
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def eliminar_producto(self, producto_id: int) -> bool:
        producto = self.get_producto(producto_id)
        if not producto:
            return False
        self.db.delete(producto)
        self.db.commit()
        return True

    # ==================== PEDIDOS & CHECKOUT ====================

    def _generar_numero_pedido(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:8].upper()
        return f"PED-{timestamp}-{short_uuid}"

    def crear_pedido(self, data: CheckoutRequest, usuario_id: int) -> Pedido:
        if not usuario_id:
            raise ValueError("Debes iniciar sesión para finalizar la compra")

        result = self.db.execute(
            select(Carrito).where(
                Carrito.site_id == self.sitio_id,
                Carrito.usuario_id == usuario_id
            )
        )
        carrito = result.scalar_one_or_none()
        
        items_carrito = []
        if carrito:
            result = self.db.execute(
                select(ItemCarrito).where(ItemCarrito.carrito_id == carrito.id)
            )
            items_carrito = list(result.scalars().all())
        
        if not items_carrito:
            raise ValueError("El carrito está vacío")
        
        subtotal = Decimal('0.0')
        items_pedido = []
        
        for item in items_carrito:
            producto = self.get_producto(item.producto_id)
            if not producto or not producto.es_activo:
                continue
            
            if producto.stock is not None:
                if producto.stock < item.cantidad:
                    raise ValueError(f"Alguien nos ganó, ya no hay stock suficiente de: {producto.nombre}")
                producto.stock -= item.cantidad
            
            item_total = Decimal(str(producto.precio)) * Decimal(str(item.cantidad))
            subtotal += item_total
            
            items_pedido.append(ItemPedido(
                producto_id=producto.id,
                nombre_producto=producto.nombre,
                sku_producto=producto.sku,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
                total=item_total
            ))
        
        if not items_pedido:
            raise ValueError("No hay productos válidos en el carrito")
        
        impuesto = round(subtotal * Decimal('0.18'), 2)
        total = subtotal + impuesto
        
        pedido = Pedido(
            site_id=self.sitio_id,
            usuario_id=usuario_id,
            numero_pedido=self._generar_numero_pedido(),
            estado=PedidoEstado.PENDIENTE,
            estado_pago=PedidoEstadoPago.PENDIENTE,
            subtotal=subtotal,
            impuesto=impuesto,
            descuento=Decimal('0.0'),
            envio=Decimal('0.0'),
            total=total,
            nombre_cliente=data.nombre_cliente,
            email_cliente=data.email_cliente,
            telefono_cliente=data.telefono_cliente,
            direccion_envio=data.direccion_envio,
            ciudad_envio=data.ciudad_envio,
            pais_envio=data.pais_envio,
            codigo_postal=data.codigo_postal,
            metodo_pago=data.metodo_pago,
            notas=data.notas
        )
        
        self.db.add(pedido)
        self.db.flush()
        
        for item in items_pedido:
            item.pedido_id = pedido.id
            self.db.add(item)
        
        if carrito:
            self.db.execute(
                delete(ItemCarrito).where(ItemCarrito.carrito_id == carrito.id)
            )
        
        self.db.commit()
        
        result_final = self.db.execute(
            select(Pedido)
            .options(joinedload(Pedido.items))
            .where(Pedido.id == pedido.id)
        )
        pedido_completo = result_final.unique().scalar_one()
        
        return pedido_completo

    def get_pedido(self, pedido_id: int) -> Pedido | None:
        result = self.db.execute(
            select(Pedido).where(
                Pedido.id == pedido_id,
                Pedido.site_id == self.sitio_id
            )
        )
        return result.scalar_one_or_none()

    def listar_pedidos(
        self,
        estado: str | None = None,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[list[Pedido], int]:
        query = select(Pedido).where(Pedido.site_id == self.sitio_id)
        if estado:
            query = query.where(Pedido.estado == estado)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Pedido.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        result = self.db.execute(query)
        return list(result.scalars().all()), total

    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: str) -> Pedido | None:
        pedido = self.get_pedido(pedido_id)
        if not pedido:
            return None
        try:
            pedido.estado = PedidoEstado(nuevo_estado)
        except ValueError:
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    # ==================== CARRITO ====================

    def obtener_o_crear_carrito(self, usuario_id: int) -> Carrito:
        result = self.db.execute(
            select(Carrito).where(
                Carrito.site_id == self.sitio_id,
                Carrito.usuario_id == usuario_id
            )
        )
        carrito = result.scalar_one_or_none()
        
        if not carrito:
            carrito = Carrito(
                site_id=self.sitio_id,
                usuario_id=usuario_id
            )
            self.db.add(carrito)
            self.db.commit()
            self.db.refresh(carrito)
        
        return carrito

    def agregar_al_carrito(
        self,
        producto_id: int,
        cantidad: int = 1,
        usuario_id: int | None = None
    ):
        if not usuario_id:
            raise ValueError("Debes iniciar sesión para agregar al carrito")

        producto = self.get_producto(producto_id)

        if not producto or not producto.es_activo:
            raise ValueError("Producto no encontrado o no disponible")

        if producto.stock is not None and producto.stock < cantidad:
            raise ValueError("Stock insuficiente")
        
        carrito = self.obtener_o_crear_carrito(usuario_id)
        
        result = self.db.execute(
            select(ItemCarrito).where(
                ItemCarrito.carrito_id == carrito.id,
                ItemCarrito.producto_id == producto_id
            )
        )
        item_existente = result.scalar_one_or_none()
        
        if item_existente:
            nueva_cantidad = item_existente.cantidad + cantidad
            if producto.stock is not None and producto.stock < nueva_cantidad:
                raise ValueError("Stock insuficiente")
            item_existente.cantidad = nueva_cantidad
            self.db.commit()
            self.db.refresh(item_existente)
        else:
            item = ItemCarrito(
                carrito_id=carrito.id,
                producto_id=producto_id,
                cantidad=cantidad
            )
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            item_existente = item
        
        return item_existente

    def actualizar_cantidad_carrito(self, item_id: int, cantidad: int) -> ItemCarrito | None:
        result = self.db.execute(
            select(ItemCarrito).where(ItemCarrito.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return None
        
        if cantidad <= 0:
            self.db.delete(item)
            self.db.commit()
            return None
        
        item.cantidad = cantidad
        self.db.commit()
        self.db.refresh(item)
        return item

    def eliminar_del_carrito(self, item_id: int) -> bool:
        result = self.db.execute(
            select(ItemCarrito).where(ItemCarrito.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True

    def obtener_carrito(self, usuario_id: int) -> Carrito | None:
        result = self.db.execute(
            select(Carrito).where(
                Carrito.site_id == self.sitio_id,
                Carrito.usuario_id == usuario_id
            )
        )
        return result.scalar_one_or_none()

