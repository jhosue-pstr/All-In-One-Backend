from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select, case
from sqlalchemy.orm import Session

from app.packages.modulos.analitica.models import Visita, Evento, Sesion
from app.packages.modulos.analitica.schemas import (
    VisitaCreate,
    EventoCreate,
    ResumenAnalitica,
    TopPagina,
    VisitaPorDia,
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

    return DashboardResponse(
        resumen=resumen,
        visitas_por_dia=visitas_por_dia,
        top_paginas=top_paginas,
        navegadores=navegadores,
        dispositivos=dispositivos,
        ultimas_visitas=[Visita for Visita in ultimas_visitas],
        eventos_recientes=[Evento for Evento in eventos_recientes],
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
    rows = db.execute(
        select(Visita.url, func.count(Visita.id))
        .where(
            Visita.site_id == site_id,
            Visita.created_at >= desde,
        )
        .group_by(Visita.url)
        .order_by(func.count(Visita.id).desc())
        .limit(limite)
    ).all()

    total = sum(row[1] for row in rows) or 1
    return [
        TopPagina(url=row[0], visitas=row[1], porcentaje=round((row[1] / total) * 100, 1))
        for row in rows
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
