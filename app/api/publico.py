from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.service.sitio import get_sitio_por_slug

router = APIRouter()


def injectar_recursos(html: str, css: str = "", js: str = "") -> str:
    if not html:
        return "<html><body><h1>Sitio en construcción</h1></body></html>"
    
    css_style = f"<style>{css}</style>" if css else ""
    js_script = f"<script>{js}</script>" if js else ""
    
    if "</head>" in html.lower():
        html = html.replace("</head>", f"{css_style}</head>", 1)
    else:
        html = f"<head>{css_style}</head>" + html
    
    if "</body>" in html.lower():
        html = html.replace("</body>", f"{js_script}</body>", 1)
    else:
        html = html + js_script
    
    return html


@router.get("/{slug}", response_class=HTMLResponse)
def render_sitio(slug: str, request: Request, db: Session = Depends(get_db)):
    sitio = get_sitio_por_slug(db, slug)
    
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    if not sitio.activo:
        raise HTTPException(status_code=403, detail="Sitio temporalmente desactivado")
    
    config = sitio.configuracion or {}
    html = config.get("html", "")
    css = config.get("css", "")
    js = config.get("js", "")
    
    html_renderizado = injectar_recursos(html, css, js)
    
    return HTMLResponse(html_renderizado)


@router.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse("<html><body><h1>AllInOne Platform</h1></body></html>")