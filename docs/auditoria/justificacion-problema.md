# Justificación, problema y oportunidad

## Necesidad de la auditoría SDLC

La auditoría SDLC se justifica porque All-InOne es una plataforma con varios elementos críticos: multitenancy, roles y permisos, módulos activables, constructor visual, auditoría, soft delete, pruebas y documentación técnica.

No basta con decir que el sistema funciona. Es necesario verificar si el desarrollo siguió un proceso ordenado y si las evidencias respaldan lo que se afirma en el informe del proyecto.

## Razones principales

<div class="section-grid" markdown>

<div class="section-card" markdown>
### Multitenancy
El sistema maneja información separada por sitio o tenant, por lo que debe verificarse que no exista acceso cruzado entre datos.
</div>

<div class="section-card" markdown>
### Arquitectura modular
La arquitectura de monolito modular debe reflejarse en la organización real del backend y frontend.
</div>

<div class="section-card" markdown>
### Seguridad
JWT, roles, permisos y rutas protegidas deben contar con evidencia técnica y pruebas suficientes.
</div>

<div class="section-card" markdown>
### Pruebas y calidad
Las pruebas funcionales, E2E, rendimiento, seguridad y análisis estático deben alinearse con los módulos críticos.
</div>

</div>

## Problema identificado

El problema no es que el sistema esté mal. El problema es que, por su complejidad, puede existir diferencia entre:

- lo documentado en el informe;
- lo planificado en Jira;
- lo implementado en backend y frontend;
- lo validado por pruebas;
- lo evidenciado por herramientas de calidad.

Por eso la auditoría busca revisar la coherencia entre esos elementos.

## Oportunidad

La auditoría representa una oportunidad para fortalecer el proyecto antes de su presentación final y futuras versiones. Permite ordenar evidencias, identificar brechas, mejorar documentación y sustentar técnicamente las decisiones tomadas.

## Beneficios esperados

| Beneficio | Explicación |
|---|---|
| Trazabilidad | Relacionar requisitos, sprints, módulos, pruebas y evidencias. |
| Calidad | Evaluar mantenibilidad, seguridad, usabilidad y funcionamiento. |
| Seguridad | Revisar autenticación, autorización, roles, permisos y aislamiento por tenant. |
| Documentación | Detectar inconsistencias entre documentos y código. |
| Mejora continua | Proponer acciones correctivas o recomendaciones para futuras versiones. |

<div class="defense-box" markdown>

**Frase para exposición:**  
“La auditoría se justifica porque All-InOne es una plataforma compleja y modular; por ello se necesita validar que la documentación, el código, las pruebas y los controles de seguridad estén alineados.”

</div>
