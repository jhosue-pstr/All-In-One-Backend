from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.usuario import User
from app.packages.modulos.analitica import schemas, services
from app.packages.modulos.analitica.services import DashboardResponse

router = APIRouter(prefix="/modules/analitica", tags=["Module: Analítica"])


@router.post("/{site_id}/visitas")
def registrar_visita(
    site_id: int,
    visita_in: schemas.VisitaCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    visita = services.registrar_visita(db, site_id, visita_in, ip, user_agent)
    return {"success": True, "data": visita}


@router.post("/{site_id}/eventos")
def registrar_evento(
    site_id: int,
    evento_in: schemas.EventoCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("analitica.crear"))],
):
    evento = services.registrar_evento(db, site_id, evento_in)
    return {"success": True, "data": evento}


@router.get("/{site_id}/dashboard", response_model=DashboardResponse)
def obtener_dashboard(
    site_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("analitica.ver"))],
    dias: int = 7,
):
    return services.obtener_dashboard(db, site_id, dias)
