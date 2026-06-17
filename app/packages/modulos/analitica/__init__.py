from app.packages.modulos.analitica.module import Module
from app.packages.modulos.analitica.models import Visita, Evento, Sesion

class AnaliticaModule(Module):
    name = "Analítica"
    slug = "analitica"
    version = "1.0.0"
    description = "Módulo de analítica y estadísticas de visitas"
    icon = "chart-bar"
    is_system = False

    def get_models(self):
        return [Visita, Evento, Sesion]

    def get_schemas(self):
        from .schemas import VisitaResponse, EventoResponse, DashboardResponse
        return [VisitaResponse, EventoResponse, DashboardResponse]

analitica_module = AnaliticaModule()
