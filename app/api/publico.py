from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)

from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session

import re
from app.db.database import get_db
from app.service.sitio import get_sitio_por_slug

router = APIRouter(
    tags=["Renderizado de Sitios"]
)

ERROR_SITIO_NO_ENCONTRADO = "Sitio no encontrado"
ERROR_SITIO_DESACTIVADO = "Sitio temporalmente desactivado"

WIDGET_SCRIPT = (
    '<script src="/static/site-widget.js" defer></script>'
)


def injectar_recursos(
    html: str,
    css: str = "",
    js: str = "",
    sitio_id: int | None = None
) -> str:
    """
    Inserta dinámicamente CSS y JavaScript
    dentro del HTML generado por el constructor visual.
    """

    if not html:
        return """
        <html>
            <body>
                <h1>Sitio en construcción</h1>
            </body>
        </html>
        """

    # Reemplazar placeholder del ID del sitio
    if sitio_id is not None:
        html = html.replace("{{SITIO_ID}}", str(sitio_id))

    css_style = (
        f"<style>{css}</style>"
        if css
        else ""
    )

    js_script = (
        f"<script>{js}</script>"
        if js
        else ""
    )

    # Insertar CSS dentro del head
    if "</head>" in html.lower():
        html = html.replace(
            "</head>",
            f"{css_style}</head>",
            1
        )
    else:
        html = f"<head>{css_style}</head>{html}"

    widget = WIDGET_SCRIPT

    # Insertar widget + JS antes del cierre del body
    scripts = f"{js_script}{widget}"
    if "</body>" in html.lower():
        html = html.replace(
            "</body>",
            f"{scripts}</body>",
            1
        )
    else:
        html = html + scripts

    return html

@router.get("/check-system")
async def check_system(db: Session = Depends(get_db)):
    return {"blog": "ok", "tienda": "ok"}

@router.get(
    "/{slug}",
    response_class=HTMLResponse,
    summary="Renderizar sitio web público",
    description="""
## Renderizado dinámico de sitios

Permite renderizar un sitio web utilizando su slug único.

### Funcionalidades
- Carga HTML dinámico
- Inserción automática de CSS
- Inyección de JavaScript personalizado
- Compatible con constructor drag & drop

### Flujo interno
1. Busca el sitio por slug
2. Obtiene configuración almacenada
3. Inserta recursos dinámicamente
4. Retorna HTML renderizado

### Resultado
Devuelve el sitio web completamente funcional.
""",
    responses={
        200: {
            "description": "Sitio renderizado correctamente"
        },
        403: {
            "description": "Sitio temporalmente desactivado"
        },
        404: {
            "description": "Sitio no encontrado"
        }
    }
)
def render_sitio(
    slug: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)]
):
    sitio = get_sitio_por_slug(
        db,
        slug
    )

    if not sitio:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_NO_ENCONTRADO
        )

    config = sitio.configuracion or {}

    # Check if a specific page is requested via query param
    page_slug = request.query_params.get("page")
    pages = config.get("pages", [])

    if page_slug and pages:
        # Look for a matching page in the pages array
        for p in pages:
            name = p.get("name", "")
            p_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            if p_slug == page_slug:
                html = p.get("html", "")
                css = p.get("css", "")
                js = config.get("js", "")
                html_renderizado = injectar_recursos(html, css, js, sitio_id=sitio.id)
                return HTMLResponse(content=html_renderizado, status_code=status.HTTP_200_OK)

    html = config.get("html", "")
    css = config.get("css", "")
    js = config.get("js", "")

    html_renderizado = injectar_recursos(
        html,
        css,
        js,
        sitio_id=sitio.id
    )

    return HTMLResponse(
        content=html_renderizado,
        status_code=status.HTTP_200_OK
    )

