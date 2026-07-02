# Supuestos y restricciones

## Supuestos

Los supuestos son condiciones que se consideran válidas para poder planificar la auditoría.

| Supuesto | Qué significa |
|---|---|
| ModularSoft colaborará con el equipo auditor. | Se espera acceso a documentación, código, reportes y aclaraciones. |
| La documentación primaria representa razonablemente el trabajo realizado. | El informe, Jira y reportes se consideran fuentes válidas. |
| El equipo auditor tendrá acceso suficiente a evidencias. | Se podrán revisar gestión, arquitectura, pruebas, seguridad y documentación. |
| Los criterios seleccionados son pertinentes. | ISO/IEC 12207, ISO/IEC 25010, CMMI-DEV y checklist SDLC aplican al proyecto. |
| El sistema se evaluará en su estado actual. | No se asumirá que funcionalidades futuras están completas. |
| Las herramientas usadas generan evidencia útil. | Jira, GitHub, Jenkins, Sonar, Snyk, Playwright, k6 y Swagger aportan sustento. |

## Restricciones

Las restricciones son límites reales de la auditoría.

| Restricción | Implicancia |
|---|---|
| Tiempo | La auditoría debe ejecutarse dentro del calendario académico. |
| Recursos | El equipo auditor tiene tiempo e integrantes limitados. |
| Acceso al entorno | Puede no existir un entorno funcional permanente. |
| Documentación disponible | Solo se evalúa con evidencias entregadas o disponibles. |
| Alcance técnico | No hay revisión línea por línea de todo el código. |
| Modificación del sistema | El auditor no corrige código ni cambia repositorios. |
| Confidencialidad | La información es de uso interno académico. |
| Pruebas avanzadas | No incluye pentesting profundo ni explotación ofensiva. |
| Académica | No es certificación oficial ni garantía productiva. |

## Diferencia entre supuesto y restricción

| Concepto | Significado | Ejemplo |
|---|---|---|
| Supuesto | Algo que se considera verdadero para poder planificar. | El equipo entregará evidencias. |
| Restricción | Un límite que no debe excederse. | No se modificará el código fuente. |

<div class="defense-box" markdown>

**Frase clave:**  
“Los supuestos permiten planificar la auditoría; las restricciones delimitan lo que realmente se puede revisar y prometer.”

</div>
