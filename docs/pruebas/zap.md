# OWASP ZAP: pruebas de seguridad

OWASP ZAP se utiliza como herramienta de apoyo para identificar riesgos de seguridad web. En el backend, su valor principal está en revisar exposición de endpoints, cabeceras, formularios, rutas y vulnerabilidades comunes desde una perspectiva automatizada.

## Tipos de escaneo

| Escaneo | Característica |
|---|---|
| Baseline | Revisión pasiva inicial, útil para detectar problemas comunes sin ataque profundo. |
| Full Scan | Escaneo más amplio, puede incluir pruebas activas. |
| API Scan | Revisión orientada a APIs mediante especificación OpenAPI/Swagger. |

## Evidencias generadas

ZAP puede producir reportes en formatos como HTML, JSON o XML. Estos reportes sirven como evidencia documental para la auditoría de seguridad.

## Qué riesgos puede ayudar a detectar

- cabeceras de seguridad ausentes;
- exposición de información sensible;
- configuraciones inseguras;
- problemas comunes de validación;
- rutas accesibles indebidamente;
- alertas relacionadas con OWASP Top 10.

## Relación con controles del backend

ZAP no reemplaza la revisión manual de código ni las pruebas de permisos. Por eso debe complementarse con revisión de JWT, RBAC, rutas protegidas, validación de entradas y aislamiento multitenant.

!!! warning "No es pentesting profundo"
    En este proyecto, ZAP debe entenderse como evidencia de revisión de seguridad automatizada. No equivale a una prueba de penetración profesional ni a explotación ofensiva avanzada.

<div class="defense-box" markdown>
**Frase para exposición:** “OWASP ZAP aporta evidencia de seguridad automatizada, pero la auditoría mantiene como restricción que no se realiza pentesting profundo.”
</div>
