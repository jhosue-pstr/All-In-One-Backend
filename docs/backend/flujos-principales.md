# Flujos principales del backend

Esta página resume los flujos más importantes que atiende el backend. No reemplaza la documentación de endpoints, pero ayuda a entender cómo se conectan los módulos y qué ocurre en una operación típica.

## 1. Inicio de sesión administrativo

```mermaid
sequenceDiagram
    participant U as Usuario interno
    participant API as /api/auth/inicio
    participant DB as Base de datos
    participant JWT as Token JWT

    U->>API: correo + contraseña
    API->>DB: buscar usuario activo
    DB-->>API: usuario encontrado
    API->>API: verificar bcrypt
    API->>JWT: generar access_token
    JWT-->>U: token Bearer
```

Este flujo permite que un usuario interno acceda al panel administrativo. El backend valida credenciales, verifica que el usuario esté activo y genera un token JWT para solicitudes posteriores.

## 2. Gestión de sitios

Un sitio representa el tenant o unidad de negocio. Las operaciones de sitios permiten crear, listar, actualizar, eliminar lógicamente y cargar miniaturas.

| Paso | Descripción |
|---|---|
| Crear sitio | Se registra la información base del tenant. |
| Listar sitios | Se recuperan sitios disponibles según usuario/permisos. |
| Actualizar sitio | Se modifican datos de configuración. |
| Asociar módulos | Se activan funcionalidades como Blog, Tienda o Analítica. |
| Cargar miniatura | Se almacena recurso visual del sitio. |

## 3. Uso de módulos activables

```mermaid
flowchart LR
    A[Sitio creado] --> B[Catálogo de módulos]
    B --> C[Activar módulo para sitio]
    C --> D[Frontend muestra funcionalidad]
    D --> E[Backend atiende rutas del módulo]
```

Este flujo conecta el core del sistema con los módulos funcionales. El sitio puede activar funcionalidades y luego operar endpoints específicos de Blog, Tienda, Auth Público o Analítica.

## 4. Publicación de contenido Blog

El módulo Blog permite administrar categorías y publicaciones. Además, separa rutas públicas y administrativas, lo cual permite mostrar solo contenido disponible al visitante y conservar estados internos como borradores o archivados.

| Vista | Qué permite |
|---|---|
| Pública | Ver posts publicados disponibles. |
| Administrativa | Crear, editar, listar estados internos y eliminar lógicamente. |

## 5. Operación de Tienda

El módulo Tienda cubre un flujo comercial básico: categorías, productos, carrito, pedidos, estado de pedido y checkout.

```mermaid
flowchart TB
    CAT[Categorías] --> PROD[Productos]
    PROD --> CART[Carrito]
    CART --> CHECK[Checkout]
    CHECK --> PED[Pedido]
    PED --> EST[Actualización de estado]
```

## 6. Registro de analítica

Analítica permite registrar visitas y eventos de un sitio. Este módulo es útil para medir interacción y alimentar dashboards administrativos.

| Endpoint conceptual | Uso |
|---|---|
| Registrar visita | Guardar página, sesión, IP, user-agent y referencia. |
| Registrar evento | Guardar interacciones relevantes del visitante. |
| Dashboard | Consultar métricas agregadas por periodo. |

<div class="defense-box" markdown>
**Frase para exposición:** “Los flujos principales muestran que el backend integra gestión administrativa, módulos de negocio, usuarios públicos y métricas bajo una misma API modular.”
</div>
