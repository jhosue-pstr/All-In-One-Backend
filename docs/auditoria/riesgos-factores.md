# Riesgos y Factores Críticos de Éxito

## Riesgos de auditoría

Los riesgos indican qué situaciones podrían afectar la calidad o suficiencia de la auditoría.

| Riesgo | Explicación simple |
|---|---|
| Documentación incompleta | Puede faltar evidencia o estar dispersa |
| Diferencia entre documentación y código | Lo descrito puede no coincidir con lo implementado |
| Pruebas incompletas | Puede que no cubran todos los flujos críticos |
| Acceso limitado al sistema | El entorno funcional puede no estar siempre disponible |
| Complejidad técnica | El sistema es modular, multitenant y tiene varias capas |
| Módulos parciales o futuros | Algunos módulos pueden estar planificados o incompletos |
| Evidencias de distintas versiones | Puede haber documentos generados en fechas diferentes |
| Seguridad no detectada | Algunos riesgos podrían requerir pruebas complementarias |

## Respuesta a riesgos

La estrategia principal consiste en revisar cada evidencia, contrastarla con el código y registrar cualquier diferencia como observación o hallazgo.

## Factores críticos de éxito

Son condiciones necesarias para que la auditoría funcione correctamente.

| Factor | Por qué es importante |
|---|---|
| Cooperación de ModularSoft | Permite obtener evidencias y aclaraciones |
| Evidencias disponibles | Sustentan los hallazgos |
| Alcance claro | Evita revisar temas fuera del objetivo |
| Criterios técnicos | Permiten evaluar con objetividad |
| Comunicación efectiva | Facilita resolver dudas |
| Comprensión de arquitectura | Ayuda a evaluar módulos, roles, permisos y multitenancy |
| Entorno funcional o evidencias equivalentes | Permite validar flujos aunque el sistema no esté siempre activo |

!!! summary "Idea clave"
    Los riesgos indican qué puede salir mal; los factores críticos indican qué debe salir bien.
