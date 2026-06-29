# OWASP ZAP

OWASP ZAP se utiliza para ejecutar pruebas dinámicas de seguridad sobre endpoints del backend.

## Propósito

Detectar posibles vulnerabilidades como:

- Errores de validación de entrada.
- Respuestas inseguras.
- Cabeceras de seguridad faltantes.
- Exposición de información.
- Comportamientos inesperados ante entradas maliciosas.

## Ubicación relacionada

```text
zap/
docker-compose.zap.yml
```

## Alcance

La revisión con ZAP corresponde a una prueba automatizada o semiautomatizada de seguridad en entorno de prueba.

!!! warning "No es pentesting completo"
    Esta validación no representa una prueba de penetración ofensiva avanzada ni una certificación formal de seguridad.

## Evidencia esperada

- URL o endpoint evaluado.
- Alertas encontradas.
- Severidad de las alertas.
- Recomendaciones.
- Estado de corrección o aceptación del riesgo.
