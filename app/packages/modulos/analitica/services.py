from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.modulo import Modulo
from app.models.sitio import Sitio
from app.packages.modulos.analitica.models import Visita, Evento, Sesion
from app.packages.modulos.blog.models import Post, Category as BlogCategory, PostStatus
from app.packages.modulos.store.models import (
    Producto, Pedido, ItemPedido, PedidoEstado,
)
from app.packages.modulos.analitica.schemas import (
    VisitaCreate,
    EventoCreate,
    ResumenAnalitica,
    TopPagina,
    VisitaPorDia,
    BlogStats,
    CategoriaPostCount,
    PostResumen,
    TiendaStats,
    ProductoVendido,
    DashboardResponse,
)

REGISTRO_NO_ENCONTRADO = "Registro no encontrado"


def registrar_visita(
    db: Session,
    site_id: int,
    visita_in: VisitaCreate,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Visita:
    navegador = _detectar_navegador(user_agent)
    dispositivo = _detectar_dispositivo(user_agent)

    visita = Visita(
        site_id=site_id,
        url=visita_in.url,
        titulo_pagina=visita_in.titulo_pagina,
        ip=ip,
        user_agent=user_agent,
        referer=visita_in.referer,
        session_id=visita_in.session_id,
        navegador=navegador,
        dispositivo=dispositivo,
    )
    db.add(visita)

    if visita_in.session_id:
        _actualizar_sesion(db, site_id, visita_in.session_id)

    db.commit()
    db.refresh(visita)
    return visita


def _actualizar_sesion(db: Session, site_id: int, session_id: str) -> None:
    result = db.execute(
        select(Sesion).where(
            Sesion.session_id == session_id,
            Sesion.site_id == site_id,
        )
    )
    sesion = result.scalar_one_or_none()

    ahora = datetime.now(timezone.utc)

    if sesion:
        sesion.fin = ahora
        sesion.paginas_vistas = Sesion.paginas_vistas + 1
        delta = (ahora - sesion.inicio).total_seconds()
        sesion.duracion_segundos = int(delta)
    else:
        sesion = Sesion(
            site_id=site_id,
            session_id=session_id,
            ip=None,
            user_agent=None,
            inicio=ahora,
            fin=ahora,
            paginas_vistas=1,
            duracion_segundos=0,
        )
        db.add(sesion)


def registrar_evento(
    db: Session,
    site_id: int,
    evento_in: EventoCreate,
) -> Evento:
    metadata = None
    if evento_in.metadata_json:
        import json
        metadata = json.dumps(evento_in.metadata_json)

    evento = Evento(
        site_id=site_id,
        session_id=evento_in.session_id,
        tipo=evento_in.tipo,
        etiqueta=evento_in.etiqueta,
        valor=evento_in.valor,
        metadata_json=metadata,
        url=evento_in.url,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


def _site_tiene_modulo(db: Session, site_id: int, slug: str) -> bool:
    sitio = db.query(Sitio).filter(Sitio.id == site_id).first()
    if not sitio:
        return False
    return any(m.slug == slug and m.activo for m in sitio.modulos)


def _obtener_blog_stats(db: Session, site_id: int) -> BlogStats | None:
    if not _site_tiene_modulo(db, site_id, "blog"):
        return None

    total = db.query(Post).filter(
        Post.site_id == site_id, Post.is_deleted == False
    ).count()

    publicados = db.query(Post).filter(
        Post.site_id == site_id,
        Post.is_deleted == False,
        Post.status == PostStatus.PUBLISHED,
    ).count()

    borradores = db.query(Post).filter(
        Post.site_id == site_id,
        Post.is_deleted == False,
        Post.status == PostStatus.DRAFT,
    ).count()

    cats = (
        db.query(BlogCategory.name, func.count(Post.id).label("total"))
        .join(Post, BlogCategory.id == Post.category_id)
        .filter(
            Post.site_id == site_id,
            Post.is_deleted == False,
            Post.category_id.isnot(None),
            BlogCategory.is_deleted == False,
        )
        .group_by(BlogCategory.name)
        .order_by(func.count(Post.id).desc())
        .all()
    )
    posts_por_categoria = [CategoriaPostCount(nombre=row[0], total=row[1]) for row in cats]

    ultimos = (
        db.query(Post.id, Post.title, Post.slug, Post.status, Post.created_at, BlogCategory.name)
        .outerjoin(BlogCategory, BlogCategory.id == Post.category_id)
        .filter(Post.site_id == site_id, Post.is_deleted == False)
        .order_by(Post.created_at.desc())
        .limit(5)
        .all()
    )
    ultimos_posts = [
        PostResumen(id=r[0], titulo=r[1], slug=r[2], estado=r[3].value, created_at=r[4], categoria=r[5])
        for r in ultimos
    ]

    return BlogStats(
        total_posts=total,
        publicados=publicados,
        borradores=borradores,
        posts_por_categoria=posts_por_categoria,
        ultimos_posts=ultimos_posts,
    )


def _obtener_tienda_stats(db: Session, site_id: int) -> TiendaStats | None:
    if not _site_tiene_modulo(db, site_id, "tienda"):
        return None

    total_productos = db.query(Producto).filter(
        Producto.site_id == site_id, Producto.es_activo == True
    ).count()

    total_pedidos = db.query(Pedido).filter(
        Pedido.site_id == site_id
    ).count()

    ingresos = (
        db.query(func.coalesce(func.sum(Pedido.total), 0))
        .filter(
            Pedido.site_id == site_id,
            Pedido.estado != PedidoEstado.CANCELADO,
        )
        .scalar()
    ) or 0

    estados = (
        db.query(Pedido.estado, func.count(Pedido.id).label("total"))
        .filter(Pedido.site_id == site_id)
        .group_by(Pedido.estado)
        .order_by(func.count(Pedido.id).desc())
        .all()
    )
    pedidos_por_estado = {str(row[0]): row[1] for row in estados}

    top = (
        db.query(
            ItemPedido.nombre_producto,
            func.sum(ItemPedido.cantidad).label("cantidad"),
            func.sum(ItemPedido.total).label("total"),
        )
        .join(Pedido, Pedido.id == ItemPedido.pedido_id)
        .filter(Pedido.site_id == site_id)
        .group_by(ItemPedido.nombre_producto)
        .order_by(func.sum(ItemPedido.cantidad).desc())
        .limit(5)
        .all()
    )
    productos_mas_vendidos = [
        ProductoVendido(nombre=r[0], cantidad=r[1], total=float(r[2]))
        for r in top
    ]

    return TiendaStats(
        total_productos=total_productos,
        total_pedidos=total_pedidos,
        ingresos_totales=float(ingresos),
        pedidos_por_estado=pedidos_por_estado,
        productos_mas_vendidos=productos_mas_vendidos,
    )


def obtener_dashboard(db: Session, site_id: int, dias: int = 7) -> DashboardResponse:
    ahora = datetime.now(timezone.utc)
    inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_periodo = ahora - timedelta(days=dias)

    visitas_hoy = db.execute(
        select(func.count(Visita.id)).where(
            Visita.site_id == site_id,
            Visita.created_at >= inicio_hoy,
        )
    ).scalar() or 0

    visitas_periodo = db.execute(
        select(func.count(Visita.id)).where(
            Visita.site_id == site_id,
            Visita.created_at >= inicio_periodo,
        )
    ).scalar() or 0

    visitantes_unicos = db.execute(
        select(func.count(func.distinct(Visita.session_id))).where(
            Visita.site_id == site_id,
            Visita.created_at >= inicio_periodo,
            Visita.session_id.isnot(None),
        )
    ).scalar() or 0

    total_visitas = db.execute(
        select(func.count(Visita.id)).where(Visita.site_id == site_id)
    ).scalar() or 0

    total_eventos = db.execute(
        select(func.count(Evento.id)).where(Evento.site_id == site_id)
    ).scalar() or 0

    sesiones_recientes = db.execute(
        select(Sesion).where(
            Sesion.site_id == site_id,
            Sesion.created_at >= inicio_periodo,
        )
    ).scalars().all()

    sesiones_con_duracion = [s for s in sesiones_recientes if s.duracion_segundos is not None]
    duracion_promedio = 0.0
    if sesiones_con_duracion:
        duracion_promedio = sum(s.duracion_segundos for s in sesiones_con_duracion) / len(sesiones_con_duracion)

    bounce_sessions = [s for s in sesiones_recientes if s.paginas_vistas == 1]
    bounce_rate = 0.0
    if sesiones_recientes:
        bounce_rate = round((len(bounce_sessions) / len(sesiones_recientes)) * 100, 1)

    visitas_7d = db.execute(
        select(func.count(Visita.id)).where(
            Visita.site_id == site_id,
            Visita.created_at >= ahora - timedelta(days=7),
        )
    ).scalar() or 0

    visitas_30d = db.execute(
        select(func.count(Visita.id)).where(
            Visita.site_id == site_id,
            Visita.created_at >= ahora - timedelta(days=30),
        )
    ).scalar() or 0

    resumen = ResumenAnalitica(
        visitas_hoy=visitas_hoy,
        visitas_7d=visitas_7d,
        visitas_30d=visitas_30d,
        visitantes_unicos=visitantes_unicos,
        bounce_rate=bounce_rate,
        duracion_promedio=duracion_promedio,
        total_visitas=total_visitas,
        total_eventos=total_eventos,
    )

    visitas_por_dia = _obtener_visitas_por_dia(db, site_id, inicio_periodo)
    top_paginas = _obtener_top_paginas(db, site_id, inicio_periodo)
    navegadores = _obtener_conteo_por_campo(db, site_id, Visita.navegador, inicio_periodo)
    dispositivos = _obtener_conteo_por_campo(db, site_id, Visita.dispositivo, inicio_periodo)

    ultimas_visitas = db.execute(
        select(Visita)
        .where(Visita.site_id == site_id)
        .order_by(Visita.created_at.desc())
        .limit(10)
    ).scalars().all()

    eventos_recientes = db.execute(
        select(Evento)
        .where(Evento.site_id == site_id)
        .order_by(Evento.created_at.desc())
        .limit(10)
    ).scalars().all()

    blog_stats = _obtener_blog_stats(db, site_id)
    tienda_stats = _obtener_tienda_stats(db, site_id)

    return DashboardResponse(
        resumen=resumen,
        visitas_por_dia=visitas_por_dia,
        top_paginas=top_paginas,
        navegadores=navegadores,
        dispositivos=dispositivos,
        ultimas_visitas=[Visita for Visita in ultimas_visitas],
        eventos_recientes=[Evento for Evento in eventos_recientes],
        blog=blog_stats,
        tienda=tienda_stats,
    )


def _obtener_visitas_por_dia(
    db: Session,
    site_id: int,
    desde: datetime,
) -> list[VisitaPorDia]:
    fecha_trunc = func.date(Visita.created_at)
    rows = db.execute(
        select(fecha_trunc, func.count(Visita.id))
        .where(
            Visita.site_id == site_id,
            Visita.created_at >= desde,
        )
        .group_by(fecha_trunc)
        .order_by(fecha_trunc)
    ).all()

    return [VisitaPorDia(fecha=str(row[0]), visitas=row[1]) for row in rows]


def _obtener_top_paginas(
    db: Session,
    site_id: int,
    desde: datetime,
    limite: int = 10,
) -> list[TopPagina]:
    count_rows = db.execute(
        select(Visita.url, func.count(Visita.id))
        .where(
            Visita.site_id == site_id,
            Visita.created_at >= desde,
        )
        .group_by(Visita.url)
        .order_by(func.count(Visita.id).desc())
        .limit(limite)
    ).all()

    if not count_rows:
        return []

    total = sum(row[1] for row in count_rows) or 1
    urls = [row[0] for row in count_rows]

    ranked = (
        select(
            Visita.url,
            Visita.titulo_pagina,
            func.row_number()
            .over(partition_by=Visita.url, order_by=Visita.created_at.desc())
            .label("rn"),
        )
        .where(Visita.url.in_(urls), Visita.site_id == site_id)
        .subquery()
    )

    latest_titles = db.execute(
        select(ranked.c.url, ranked.c.titulo_pagina).where(ranked.c.rn == 1)
    ).all()

    title_map = {r[0]: r[1] for r in latest_titles}

    return [
        TopPagina(
            url=row[0],
            titulo_pagina=title_map.get(row[0]),
            visitas=row[1],
            porcentaje=round((row[1] / total) * 100, 1),
        )
        for row in count_rows
    ]


def _obtener_conteo_por_campo(
    db: Session,
    site_id: int,
    campo,
    desde: datetime,
) -> dict[str, int]:
    rows = db.execute(
        select(campo, func.count(Visita.id))
        .where(
            Visita.site_id == site_id,
            Visita.created_at >= desde,
            campo.isnot(None),
        )
        .group_by(campo)
        .order_by(func.count(Visita.id).desc())
    ).all()

    return {row[0] or "Otros": row[1] for row in rows}


def _detectar_navegador(user_agent: Optional[str]) -> Optional[str]:
    if not user_agent:
        return None
    ua = user_agent.lower()
    if "chrome" in ua and "edge" not in ua:
        return "Chrome"
    if "edge" in ua:
        return "Edge"
    if "firefox" in ua:
        return "Firefox"
    if "safari" in ua:
        return "Safari"
    if "opera" in ua or "opr" in ua:
        return "Opera"
    return "Otros"


def _detectar_dispositivo(user_agent: Optional[str]) -> Optional[str]:
    if not user_agent:
        return None
    ua = user_agent.lower()
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        return "Móvil"
    if "tablet" in ua or "ipad" in ua:
        return "Tablet"
    return "Desktop"
