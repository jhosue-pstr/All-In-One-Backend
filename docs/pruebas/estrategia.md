# Estrategia de pruebas del backend

La estrategia de pruebas del backend combina validaciones funcionales, pruebas automatizadas de API, pruebas de rendimiento, pruebas de seguridad y análisis dentro del flujo de integración continua. El objetivo es demostrar que el backend no solo fue desarrollado, sino también validado con evidencias técnicas.

## Tipos de pruebas consideradas

| Tipo | Herramienta / Evidencia | Qué valida |
|---|---|---|
| API / funcional | Pytest + HTTPX/TestClient | Endpoints, respuestas, errores, permisos y reglas de negocio. |
| Servicios | Pytest | Lógica interna sin depender solo de la capa HTTP. |
| Base de datos | Pytest | Conexión, seeds y comportamiento de persistencia. |
| Rendimiento | k6 | Carga, estrés, picos y resistencia. |
| Seguridad | OWASP ZAP | Riesgos web comunes sobre endpoints o aplicación objetivo. |
| Calidad / CI | Jenkins, coverage, análisis estático | Automatización, métricas y control técnico. |

## Estructura de pruebas automatizadas

```text
test/
├── api/        # Pruebas de endpoints
├── core/       # Componentes transversales
├── db/         # Base de datos y seeds
├── models/     # Modelos SQLAlchemy
├── schemas/    # Esquemas Pydantic
└── service/    # Reglas de negocio
```

## Flujos críticos a validar

- autenticación interna y uso de JWT;
- gestión de sitios y plantillas;
- activación/desactivación de módulos;
- permisos y roles;
- Blog: categorías, posts y estados;
- Tienda: productos, categorías, carrito y pedidos;
- Auth Público: usuario final por sitio;
- Analítica: visitas, eventos y dashboard;
- auditoría y soft delete.

## Relación con el checklist SDLC

Las pruebas del backend sustentan principalmente el bloque **CL-04 Procedimientos de Prueba**, pero también ayudan a defender criterios de calidad, seguridad, mantenibilidad e implementación técnica.

!!! info "Punto importante"
    Que existan pruebas no significa que cubran absolutamente todo. La auditoría debe revisar alcance, resultados y brechas de cobertura.

<div class="decision-box" markdown>
**Idea clave:** la estrategia de pruebas combina evidencia automatizada y no funcional para demostrar calidad técnica del backend dentro del ciclo SDLC.
</div>
