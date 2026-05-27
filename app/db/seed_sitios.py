"""Seed de sitios demo: landing abogado, blog, tienda"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.sitio import Sitio
from app.packages.modulos.blog.models import Category as BlogCategory, Post, PostStatus
from app.packages.modulos.store.models import Categoria as TiendaCategoria, Producto


def seed_sitios():
    sitios_data = [
        {
            "slug": "abogado-demo",
            "nombre": "Estudio Jurídico Pérez & Asociados",
            "activo": True,
            "configuracion": {
                "html": ABOGADO_HTML,
                "css": "",
                "js": "",
            },
            "switches": {},
        },
        {
            "slug": "blog-demo",
            "nombre": "Blog de Noticias",
            "activo": True,
            "configuracion": {
                "html": BLOG_HTML,
                "css": "",
                "js": "",
            },
            "switches": {},
        },
        {
            "slug": "tienda-demo",
            "nombre": "Mi Tienda Online",
            "activo": True,
            "configuracion": {
                "html": TIENDA_HTML,
                "css": "",
                "js": "",
            },
            "switches": {},
        },
    ]

    with Session(engine) as db:
        for i, data in enumerate(sitios_data):
            slug = data["slug"]
            existente = db.query(Sitio).filter(Sitio.slug == slug).first()
            if existente:
                print(f"  Sitio '{slug}' ya existe (id={existente.id})")
                sitio_id = existente.id
            else:
                sitio = Sitio(**data)
                db.add(sitio)
                db.flush()
                sitio_id = sitio.id
                print(f"  Sitio '{slug}' creado (id={sitio_id})")

            # Seed data according to site type
            if slug == "blog-demo":
                seed_blog_data(db, sitio_id)
            elif slug == "tienda-demo":
                seed_tienda_data(db, sitio_id)

        db.commit()
    print(" Seed de sitios completado")


def seed_blog_data(db: Session, sitio_id: int):
    """Create sample categories and posts for the blog demo site."""

    # Check if data already exists
    existing = db.query(BlogCategory).filter(BlogCategory.site_id == sitio_id).first()
    if existing:
        print(f"    Blog data for sitio {sitio_id} already exists, skipping")
        return

    # Create categories
    cat_general = BlogCategory(site_id=sitio_id, name="General", slug="general", description="Artículos generales")
    cat_tech = BlogCategory(site_id=sitio_id, name="Tecnología", slug="tecnologia", description="Noticias de tecnología")
    cat_tips = BlogCategory(site_id=sitio_id, name="Consejos", slug="consejos", description="Consejos útiles")
    db.add_all([cat_general, cat_tech, cat_tips])
    db.flush()

    now = datetime.now(timezone.utc)

    posts = [
        Post(
            site_id=sitio_id, category_id=cat_general.id,
            title="Bienvenido a nuestro Blog",
            slug="bienvenido-a-nuestro-blog",
            content="<p>Este es el primer artículo de nuestro blog. Aquí compartiremos contenido interesante y relevante para nuestra comunidad.</p><p>Esperamos que disfruten leyendo nuestros artículos tanto como nosotros disfrutamos creándolos.</p>",
            excerpt="Descubre todo lo que tenemos preparado para ti en nuestro nuevo blog.",
            featured_image="https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&q=80",
            status=PostStatus.PUBLISHED,
            published_at=now,
        ),
        Post(
            site_id=sitio_id, category_id=cat_tech.id,
            title="Las últimas tendencias tecnológicas del 2026",
            slug="tendencias-tecnologicas-2026",
            content="<p>La tecnología avanza a pasos agigantados. En este artículo exploramos las tendencias más importantes que están marcando el rumbo de la industria.</p><p>Desde inteligencia artificial hasta computación cuántica, el futuro ya está aquí.</p>",
            excerpt="Explora las tendencias tecnológicas que están transformando el mundo en 2026.",
            featured_image="https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
            status=PostStatus.PUBLISHED,
            published_at=now,
        ),
        Post(
            site_id=sitio_id, category_id=cat_tips.id,
            title="10 consejos para mejorar tu productividad",
            slug="consejos-productividad",
            content="<p>La productividad no se trata de hacer más en menos tiempo, sino de hacer las cosas correctas. Aquí tienes 10 consejos prácticos.</p><p>1. <strong>Planifica tu día</strong><br>Dedica 10 minutos cada mañana a planificar tus tareas.</p><p>2. <strong>Elimina distracciones</strong><br>Apaga notificaciones y enfócate en una tarea a la vez.</p>",
            excerpt="Mejora tu productividad con estos consejos prácticos y fáciles de implementar.",
            featured_image="https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&q=80",
            status=PostStatus.PUBLISHED,
            published_at=now,
        ),
        Post(
            site_id=sitio_id, category_id=cat_general.id,
            title="Cómo empezar con éxito tu proyecto online",
            slug="empezar-proyecto-online",
            content="<p>Iniciar un proyecto online puede ser abrumador, pero con la estrategia correcta, puedes lograr el éxito.</p><p>En este artículo te guiamos paso a paso para que tu proyecto despegue.</p>",
            excerpt="Guía completa para lanzar tu proyecto online con el pie derecho.",
            featured_image="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
            status=PostStatus.PUBLISHED,
            published_at=now,
        ),
    ]
    db.add_all(posts)
    print(f"    Blog: {len(posts)} posts y 3 categorías creados")


def seed_tienda_data(db: Session, sitio_id: int):
    """Create sample categories and products for the tienda demo site."""

    existing = db.query(TiendaCategoria).filter(TiendaCategoria.site_id == sitio_id).first()
    if existing:
        print(f"    Tienda data for sitio {sitio_id} already exists, skipping")
        return

    # Create categories
    cat_electronica = TiendaCategoria(
        site_id=sitio_id, nombre="Electrónicos", slug="electronicos",
        descripcion="Los mejores dispositivos electrónicos", orden=1, activa=True,
    )
    cat_ropa = TiendaCategoria(
        site_id=sitio_id, nombre="Ropa y Accesorios", slug="ropa-accesorios",
        descripcion="Moda para todos los estilos", orden=2, activa=True,
    )
    cat_hogar = TiendaCategoria(
        site_id=sitio_id, nombre="Hogar", slug="hogar",
        descripcion="Todo para tu casa", orden=3, activa=True,
    )
    db.add_all([cat_electronica, cat_ropa, cat_hogar])
    db.flush()

    products = [
        Producto(
            site_id=sitio_id, categoria_id=cat_electronica.id,
            nombre="Auriculares Bluetooth Pro",
            slug="auriculares-bluetooth-pro",
            descripcion="Auriculares inalámbricos con cancelación de ruido activa y 30 horas de batería. Sonido de alta fidelidad.",
            sku="AUD-BT-001",
            precio=199.90, precio_comparacion=249.90,
            stock=50, stock_minimo=5,
            imagenes=["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80"],
            es_activo=True, es_featured=True,
        ),
        Producto(
            site_id=sitio_id, categoria_id=cat_electronica.id,
            nombre="Smartwatch Deportivo X200",
            slug="smartwatch-deportivo-x200",
            descripcion="Reloj inteligente con GPS, monitor cardíaco y resistencia al agua. Ideal para deportistas.",
            sku="SW-X200-002",
            precio=349.90, precio_comparacion=None,
            stock=30, stock_minimo=3,
            imagenes=["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80"],
            es_activo=True, es_featured=False,
        ),
        Producto(
            site_id=sitio_id, categoria_id=cat_ropa.id,
            nombre="Chaqueta Urbana Negra",
            slug="chaqueta-urbana-negra",
            descripcion="Chaqueta moderna con diseño minimalista. Ideal para el día a día.",
            sku="ROP-CH-003",
            precio=129.90, precio_comparacion=159.90,
            stock=80, stock_minimo=10,
            imagenes=["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=80"],
            es_activo=True, es_featured=False,
        ),
        Producto(
            site_id=sitio_id, categoria_id=cat_hogar.id,
            nombre="Lámpara LED Inteligente",
            slug="lampara-led-inteligente",
            descripcion="Lámpara con control por voz, 16 millones de colores y programación horaria.",
            sku="HOG-LED-004",
            precio=89.90, precio_comparacion=None,
            stock=120, stock_minimo=15,
            imagenes=["https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=600&q=80"],
            es_activo=True, es_featured=False,
        ),
        Producto(
            site_id=sitio_id, categoria_id=cat_electronica.id,
            nombre="Cámara Web 4K Ultra HD",
            slug="camara-web-4k-ultra-hd",
            descripcion="Cámara con resolución 4K, micrófono incorporado y enfoque automático. Perfecta para videollamadas.",
            sku="CAM-4K-005",
            precio=159.90, precio_comparacion=199.90,
            stock=45, stock_minimo=5,
            imagenes=["https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80"],
            es_activo=True, es_featured=False,
        ),
        Producto(
            site_id=sitio_id, categoria_id=cat_ropa.id,
            nombre="Mochila Ejecutiva Premium",
            slug="mochila-ejecutiva-premium",
            descripcion="Mochila con compartimento para laptop de 15.6, puerto USB y diseño elegante.",
            sku="ROP-MO-006",
            precio=99.90, precio_comparacion=None,
            stock=65, stock_minimo=8,
            imagenes=["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80"],
            es_activo=True, es_featured=False,
        ),
    ]
    db.add_all(products)
    print(f"    Tienda: {len(products)} productos y 3 categorías creados")


# ==================== HTML TEMPLATES ====================

ABOGADO_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Estudio Jurídico Pérez & Asociados</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>

  <!-- HEADER / NAVBAR -->
  <header style="padding:15px 40px;display:flex;align-items:center;justify-content:space-between;background:#1e293b;color:white;position:sticky;top:0;z-index:100;">
    <div style="font-size:22px;font-weight:700;color:#fbbf24;">Pérez & Asociados</div>
    <nav style="display:flex;gap:25px;">
      <a href="#inicio" style="color:white;text-decoration:none;font-size:14px;">Inicio</a>
      <a href="#servicios" style="color:white;text-decoration:none;font-size:14px;">Servicios</a>
      <a href="#nosotros" style="color:white;text-decoration:none;font-size:14px;">Nosotros</a>
      <a href="#testimonios" style="color:white;text-decoration:none;font-size:14px;">Testimonios</a>
      <a href="#faq" style="color:white;text-decoration:none;font-size:14px;">FAQ</a>
      <a href="#contacto" style="color:white;text-decoration:none;font-size:14px;">Contacto</a>
    </nav>
  </header>

  <!-- HERO -->
  <section id="inicio" style="padding:100px 20px;background:linear-gradient(135deg,#1e293b 0%,#334155 100%);text-align:center;color:white;">
    <h1 style="font-size:52px;font-weight:700;margin:0 0 20px 0;line-height:1.1;">Protegiendo tus derechos<br>con <span style="color:#fbbf24;">excelencia jurídica</span></h1>
    <p style="font-size:20px;margin:0 0 35px 0;opacity:0.9;max-width:600px;margin-left:auto;margin-right:auto;">Más de 20 años de experiencia brindando asesoría legal especializada a personas y empresas. Tu tranquilidad es nuestra prioridad.</p>
    <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">
      <a href="#contacto" style="display:inline-block;padding:16px 36px;background:#fbbf24;color:#1e293b;border-radius:8px;text-decoration:none;font-weight:700;font-size:16px;">Agenda tu consulta gratis</a>
      <a href="#servicios" style="display:inline-block;padding:16px 36px;background:transparent;color:white;border:2px solid white;border-radius:8px;text-decoration:none;font-weight:600;font-size:16px;">Nuestros servicios</a>
    </div>
  </section>

  <!-- SERVICIOS -->
  <section id="servicios" style="padding:70px 20px;background:#f8fafc;">
    <h2 style="text-align:center;margin:0 0 15px 0;font-size:34px;color:#0f172a;">Áreas de Práctica</h2>
    <p style="text-align:center;margin:0 0 45px 0;color:#64748b;font-size:16px;">Ofrecemos asesoría integral en las siguientes áreas del derecho</p>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:30px;max-width:1000px;margin:0 auto;">
      <div style="padding:35px 25px;background:white;border-radius:14px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.06);border-top:4px solid #fbbf24;">
        <div style="font-size:44px;margin-bottom:18px;color:#fbbf24;">&#9878;</div>
        <h3 style="margin:0 0 12px 0;font-size:20px;color:#0f172a;">Derecho Civil</h3>
        <p style="margin:0;color:#64748b;font-size:14px;line-height:1.7;">Contratos, sucesiones, propiedad y obligaciones. Defendemos tus derechos patrimoniales y personales.</p>
      </div>
      <div style="padding:35px 25px;background:white;border-radius:14px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.06);border-top:4px solid #fbbf24;">
        <div style="font-size:44px;margin-bottom:18px;color:#fbbf24;">&#9881;</div>
        <h3 style="margin:0 0 12px 0;font-size:20px;color:#0f172a;">Derecho Corporativo</h3>
        <p style="margin:0;color:#64748b;font-size:14px;line-height:1.7;">Constitución de empresas, fusiones, contratos comerciales y gobierno corporativo.</p>
      </div>
      <div style="padding:35px 25px;background:white;border-radius:14px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.06);border-top:4px solid #fbbf24;">
        <div style="font-size:44px;margin-bottom:18px;color:#fbbf24;">&#9879;</div>
        <h3 style="margin:0 0 12px 0;font-size:20px;color:#0f172a;">Derecho Laboral</h3>
        <p style="margin:0;color:#64748b;font-size:14px;line-height:1.7;">Asesoría a empresas y trabajadores en relaciones laborales, despidos y negociaciones colectivas.</p>
      </div>
      <div style="padding:35px 25px;background:white;border-radius:14px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.06);border-top:4px solid #fbbf24;">
        <div style="font-size:44px;margin-bottom:18px;color:#fbbf24;">&#9883;</div>
        <h3 style="margin:0 0 12px 0;font-size:20px;color:#0f172a;">Derecho Tributario</h3>
        <p style="margin:0;color:#64748b;font-size:14px;line-height:1.7;">Planificación fiscal, defensa ante SUNAT y cumplimiento de obligaciones tributarias.</p>
      </div>
      <div style="padding:35px 25px;background:white;border-radius:14px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.06);border-top:4px solid #fbbf24;">
        <div style="font-size:44px;margin-bottom:18px;color:#fbbf24;">&#9876;</div>
        <h3 style="margin:0 0 12px 0;font-size:20px;color:#0f172a;">Derecho Penal</h3>
        <p style="margin:0;color:#64748b;font-size:14px;line-height:1.7;">Defensa penal estratégica en todas las instancias. Protegemos tu libertad y reputación.</p>
      </div>
      <div style="padding:35px 25px;background:white;border-radius:14px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.06);border-top:4px solid #fbbf24;">
        <div style="font-size:44px;margin-bottom:18px;color:#fbbf24;">&#9829;</div>
        <h3 style="margin:0 0 12px 0;font-size:20px;color:#0f172a;">Derecho de Familia</h3>
        <p style="margin:0;color:#64748b;font-size:14px;line-height:1.7;">Divorcios, tenencia, alimentos y todo lo relacionado al derecho familiar.</p>
      </div>
    </div>
  </section>

  <!-- NOSOTROS -->
  <section id="nosotros" style="padding:70px 20px;display:flex;gap:50px;align-items:center;max-width:1000px;margin:0 auto;">
    <img src="https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=500&q=80" alt="Estudio Jurídico" style="width:450px;height:400px;object-fit:cover;border-radius:16px;flex-shrink:0;box-shadow:0 10px 40px rgba(0,0,0,0.1);">
    <div>
      <span style="display:inline-block;padding:6px 14px;background:#fef3c7;color:#92400e;font-size:12px;font-weight:700;border-radius:999px;margin-bottom:15px;">Sobre Nosotros</span>
      <h2 style="margin:0 0 20px 0;font-size:34px;color:#0f172a;">Más de 20 años<br>de experiencia jurídica</h2>
      <p style="margin:0 0 15px 0;color:#475569;line-height:1.7;font-size:15px;">En Pérez & Asociados, nos enorgullece ofrecer un servicio legal de excelencia, respaldado por un equipo de abogados altamente especializados y con amplia experiencia en diversas ramas del derecho.</p>
      <p style="margin:0 0 15px 0;color:#475569;line-height:1.7;font-size:15px;">Nuestra filosofía es clara: poner al cliente en el centro de cada decisión, brindando asesoría personalizada y estratégica para cada caso.</p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:25px;">
        <div style="padding:15px;background:#f8fafc;border-radius:10px;text-align:center;">
          <strong style="display:block;font-size:28px;color:#fbbf24;">500+</strong>
          <span style="color:#64748b;font-size:13px;">Casos exitosos</span>
        </div>
        <div style="padding:15px;background:#f8fafc;border-radius:10px;text-align:center;">
          <strong style="display:block;font-size:28px;color:#fbbf24;">98%</strong>
          <span style="color:#64748b;font-size:13px;">Casos ganados</span>
        </div>
        <div style="padding:15px;background:#f8fafc;border-radius:10px;text-align:center;">
          <strong style="display:block;font-size:28px;color:#fbbf24;">12</strong>
          <span style="color:#64748b;font-size:13px;">Abogados expertos</span>
        </div>
        <div style="padding:15px;background:#f8fafc;border-radius:10px;text-align:center;">
          <strong style="display:block;font-size:28px;color:#fbbf24;">20+</strong>
          <span style="color:#64748b;font-size:13px;">Años de experiencia</span>
        </div>
      </div>
    </div>
  </section>

  <!-- FEATURES -->
  <section style="padding:60px 20px;background:#f8fafc;">
    <h2 style="text-align:center;margin:0 0 40px 0;font-size:32px;color:#0f172a;">¿Por qué elegirnos?</h2>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:25px;max-width:800px;margin:0 auto;">
      <div style="display:flex;gap:15px;align-items:flex-start;background:white;padding:20px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.04);">
        <i class="fa fa-check-circle" style="font-size:24px;color:#fbbf24;margin-top:3px;"></i>
        <div>
          <strong style="display:block;font-size:17px;color:#0f172a;">Atención Personalizada</strong>
          <span style="color:#64748b;font-size:14px;">Cada caso es único. Te asignamos un abogado dedicado que conocerá tu situación a fondo.</span>
        </div>
      </div>
      <div style="display:flex;gap:15px;align-items:flex-start;background:white;padding:20px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.04);">
        <i class="fa fa-bolt" style="font-size:24px;color:#fbbf24;margin-top:3px;"></i>
        <div>
          <strong style="display:block;font-size:17px;color:#0f172a;">Respuesta Rápida</strong>
          <span style="color:#64748b;font-size:14px;">Te respondemos en menos de 24 horas. Sabemos que en temas legales, el tiempo es crucial.</span>
        </div>
      </div>
      <div style="display:flex;gap:15px;align-items:flex-start;background:white;padding:20px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.04);">
        <i class="fa fa-shield" style="font-size:24px;color:#fbbf24;margin-top:3px;"></i>
        <div>
          <strong style="display:block;font-size:17px;color:#0f172a;">Confidencialidad Total</strong>
          <span style="color:#64748b;font-size:14px;">Toda la información compartida está protegida por el secreto profesional abogado-cliente.</span>
        </div>
      </div>
      <div style="display:flex;gap:15px;align-items:flex-start;background:white;padding:20px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.04);">
        <i class="fa fa-trophy" style="font-size:24px;color:#fbbf24;margin-top:3px;"></i>
        <div>
          <strong style="display:block;font-size:17px;color:#0f172a;">Trayectoria Comprobada</strong>
          <span style="color:#64748b;font-size:14px;">Más de 500 casos exitosos y un 98% de satisfacción de nuestros clientes.</span>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section style="padding:60px 20px;background:linear-gradient(135deg,#1e293b,#334155);text-align:center;color:white;">
    <h2 style="margin:0 0 15px 0;font-size:34px;">¿Necesitas asesoría legal?</h2>
    <p style="margin:0 0 25px 0;font-size:18px;opacity:0.9;">No esperes más. Contáctanos hoy y agenda una consulta gratuita.</p>
    <a href="#contacto" style="display:inline-block;padding:16px 40px;background:#fbbf24;color:#1e293b;border-radius:8px;text-decoration:none;font-weight:700;font-size:18px;">Solicitar Consulta Gratis</a>
  </section>

  <!-- TESTIMONIOS -->
  <section id="testimonios" style="padding:70px 20px;background:white;">
    <h2 style="text-align:center;margin:0 0 45px 0;font-size:34px;color:#0f172a;">Lo que dicen nuestros clientes</h2>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:25px;max-width:1000px;margin:0 auto;">
      <div style="padding:30px;background:#f8fafc;border-radius:14px;border:1px solid #e2e8f0;">
        <i class="fa fa-quote-left" style="color:#fbbf24;font-size:24px;"></i>
        <p style="margin:15px 0;font-style:italic;color:#475569;font-size:14px;line-height:1.7;">"El equipo de Pérez & Asociados me ayudó a resolver un caso complejo de manera rápida y eficiente. Altamente recomendados."</p>
        <div style="display:flex;align-items:center;gap:12px;">
          <img src="https://placehold.co/50x50/fbbf24/1e293b?text=M" alt="Cliente" style="width:44px;height:44px;border-radius:50%;">
          <div>
            <strong style="font-size:14px;color:#0f172a;">María García</strong>
            <p style="margin:0;color:#94a3b8;font-size:12px;">Cliente</p>
          </div>
        </div>
      </div>
      <div style="padding:30px;background:#f8fafc;border-radius:14px;border:1px solid #e2e8f0;">
        <i class="fa fa-quote-left" style="color:#fbbf24;font-size:24px;"></i>
        <p style="margin:15px 0;font-style:italic;color:#475569;font-size:14px;line-height:1.7;">"Excelente asesoría corporativa. Gracias a ellos pudimos estructurar nuestra empresa de forma sólida y segura."</p>
        <div style="display:flex;align-items:center;gap:12px;">
          <img src="https://placehold.co/50x50/fbbf24/1e293b?text=C" alt="Cliente" style="width:44px;height:44px;border-radius:50%;">
          <div>
            <strong style="font-size:14px;color:#0f172a;">Carlos Mendoza</strong>
            <p style="margin:0;color:#94a3b8;font-size:12px;">Empresario</p>
          </div>
        </div>
      </div>
      <div style="padding:30px;background:#f8fafc;border-radius:14px;border:1px solid #e2e8f0;">
        <i class="fa fa-quote-left" style="color:#fbbf24;font-size:24px;"></i>
        <p style="margin:15px 0;font-style:italic;color:#475569;font-size:14px;line-height:1.7;">"Profesionalismo y dedicación en cada paso. Me sentí acompañada durante todo el proceso legal. Muy agradecida."</p>
        <div style="display:flex;align-items:center;gap:12px;">
          <img src="https://placehold.co/50x50/fbbf24/1e293b?text=A" alt="Cliente" style="width:44px;height:44px;border-radius:50%;">
          <div>
            <strong style="font-size:14px;color:#0f172a;">Ana Torres</strong>
            <p style="margin:0;color:#94a3b8;font-size:12px;">Cliente</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section id="faq" style="padding:70px 20px;background:#f8fafc;max-width:800px;margin:0 auto;">
    <h2 style="text-align:center;margin:0 0 40px 0;font-size:34px;color:#0f172a;">Preguntas Frecuentes</h2>
    <div style="margin-bottom:15px;border:1px solid #e2e8f0;border-radius:10px;padding:22px;background:white;">
      <strong style="font-size:16px;color:#0f172a;">¿Cuánto cuesta una consulta inicial?</strong>
      <p style="margin:12px 0 0 0;color:#64748b;font-size:14px;line-height:1.7;">La primera consulta es completamente gratuita. En ella evaluamos tu caso y te explicamos las opciones legales disponibles.</p>
    </div>
    <div style="margin-bottom:15px;border:1px solid #e2e8f0;border-radius:10px;padding:22px;background:white;">
      <strong style="font-size:16px;color:#0f172a;">¿Cuánto tiempo toma resolver un caso?</strong>
      <p style="margin:12px 0 0 0;color:#64748b;font-size:14px;line-height:1.7;">Depende de la complejidad y tipo de caso. Te daremos un estimado realista durante la consulta inicial.</p>
    </div>
    <div style="margin-bottom:15px;border:1px solid #e2e8f0;border-radius:10px;padding:22px;background:white;">
      <strong style="font-size:16px;color:#0f172a;">¿Ofrecen servicios para empresas?</strong>
      <p style="margin:12px 0 0 0;color:#64748b;font-size:14px;line-height:1.7;">Sí, contamos con un área especializada en derecho corporativo. Asesoramos desde startups hasta grandes corporaciones.</p>
    </div>
    <div style="border:1px solid #e2e8f0;border-radius:10px;padding:22px;background:white;">
      <strong style="font-size:16px;color:#0f172a;">¿Cómo puedo agendar una cita?</strong>
      <p style="margin:12px 0 0 0;color:#64748b;font-size:14px;line-height:1.7;">Puedes usar el formulario de contacto, llamarnos al +51 999 888 777 o escribirnos a contacto@perezasociados.pe</p>
    </div>
  </section>

  <!-- CONTACTO -->
  <section id="contacto" style="padding:70px 20px;background:white;">
    <h2 style="text-align:center;margin:0 0 15px 0;font-size:34px;color:#0f172a;">Contáctanos</h2>
    <p style="text-align:center;margin:0 0 40px 0;color:#64748b;font-size:16px;">Déjanos tus datos y te llamaremos para agendar tu consulta gratuita</p>
    <form style="max-width:520px;margin:0 auto;display:flex;flex-direction:column;gap:16px;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <input type="text" placeholder="Tu nombre" style="padding:14px;border:1px solid #e2e8f0;border-radius:10px;font-size:15px;outline:none;">
        <input type="email" placeholder="Tu email" style="padding:14px;border:1px solid #e2e8f0;border-radius:10px;font-size:15px;outline:none;">
      </div>
      <input type="tel" placeholder="Tu teléfono" style="padding:14px;border:1px solid #e2e8f0;border-radius:10px;font-size:15px;outline:none;">
      <select style="padding:14px;border:1px solid #e2e8f0;border-radius:10px;font-size:15px;outline:none;color:#475569;">
        <option value="">Selecciona un área legal</option>
        <option>Derecho Civil</option>
        <option>Derecho Corporativo</option>
        <option>Derecho Laboral</option>
        <option>Derecho Tributario</option>
        <option>Derecho Penal</option>
        <option>Derecho de Familia</option>
        <option>Otro</option>
      </select>
      <textarea placeholder="Cuéntanos brevemente tu caso" rows="4" style="padding:14px;border:1px solid #e2e8f0;border-radius:10px;font-size:15px;resize:vertical;outline:none;"></textarea>
      <button type="submit" style="padding:16px;background:#fbbf24;color:#1e293b;border:none;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer;">Enviar Mensaje</button>
    </form>
    <div style="text-align:center;margin-top:40px;color:#64748b;font-size:15px;">
      <p style="margin:5px 0;"><i class="fa fa-map-marker" style="color:#fbbf24;"></i> Av. La Legalidad 456, Lima</p>
      <p style="margin:5px 0;"><i class="fa fa-phone" style="color:#fbbf24;"></i> +51 999 888 777</p>
      <p style="margin:5px 0;"><i class="fa fa-envelope" style="color:#fbbf24;"></i> contacto@perezasociados.pe</p>
      <p style="margin:5px 0;"><i class="fa fa-clock" style="color:#fbbf24;"></i> Lun-Vie: 9:00am - 6:00pm</p>
    </div>
  </section>

  <!-- FOOTER -->
  <footer style="padding:40px 20px 20px;background:#0f172a;color:white;">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:30px;max-width:1000px;margin:0 auto 30px auto;">
      <div>
        <strong style="font-size:18px;display:block;margin-bottom:15px;color:#fbbf24;">Pérez & Asociados</strong>
        <p style="margin:0;font-size:13px;opacity:0.7;line-height:1.7;">Estudio jurídico con más de 20 años de experiencia brindando asesoría legal de excelencia.</p>
      </div>
      <div>
        <strong style="font-size:15px;display:block;margin-bottom:15px;color:white;">Enlaces</strong>
        <div style="display:flex;flex-direction:column;gap:8px;font-size:13px;">
          <a href="#inicio" style="color:white;opacity:0.7;text-decoration:none;">Inicio</a>
          <a href="#servicios" style="color:white;opacity:0.7;text-decoration:none;">Servicios</a>
          <a href="#nosotros" style="color:white;opacity:0.7;text-decoration:none;">Nosotros</a>
          <a href="#contacto" style="color:white;opacity:0.7;text-decoration:none;">Contacto</a>
        </div>
      </div>
      <div>
        <strong style="font-size:15px;display:block;margin-bottom:15px;color:white;">Áreas</strong>
        <div style="display:flex;flex-direction:column;gap:8px;font-size:13px;">
          <span style="opacity:0.7;">Derecho Civil</span>
          <span style="opacity:0.7;">Derecho Corporativo</span>
          <span style="opacity:0.7;">Derecho Laboral</span>
          <span style="opacity:0.7;">Derecho Penal</span>
        </div>
      </div>
      <div>
        <strong style="font-size:15px;display:block;margin-bottom:15px;color:white;">Síguenos</strong>
        <div style="display:flex;gap:12px;font-size:22px;">
          <i class="fa fa-facebook" style="opacity:0.7;cursor:pointer;"></i>
          <i class="fa fa-instagram" style="opacity:0.7;cursor:pointer;"></i>
          <i class="fa fa-linkedin" style="opacity:0.7;cursor:pointer;"></i>
          <i class="fa fa-twitter" style="opacity:0.7;cursor:pointer;"></i>
        </div>
      </div>
    </div>
    <div style="text-align:center;border-top:1px solid #1e293b;padding-top:20px;font-size:13px;opacity:0.6;">
      &copy; 2026 Pérez & Asociados. Todos los derechos reservados.
    </div>
  </footer>

</body>
</html>"""


BLOG_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog de Noticias</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}
  </style>
</head>
<body>

  <!-- NAVBAR -->
  <header style="padding:15px 40px;display:flex;align-items:center;justify-content:space-between;background:#0f172a;color:white;position:sticky;top:0;z-index:100;">
    <div style="font-size:22px;font-weight:700;color:#2563eb;">Blog News</div>
    <nav style="display:flex;gap:25px;">
      <a href="#" style="color:white;text-decoration:none;font-size:14px;">Inicio</a>
      <a href="#" style="color:white;text-decoration:none;font-size:14px;">Blog</a>
      <a href="#" style="color:white;text-decoration:none;font-size:14px;">Categorías</a>
      <a href="#" style="color:white;text-decoration:none;font-size:14px;">Contacto</a>
    </nav>
  </header>

  <!-- HERO -->
  <section style="padding:80px 20px;background:linear-gradient(135deg,#0f172a,#1e3a5f);text-align:center;color:white;">
    <h1 style="font-size:44px;font-weight:700;margin:0 0 16px 0;">Nuestro Blog</h1>
    <p style="font-size:18px;opacity:0.85;max-width:500px;margin:0 auto;">Descubre artículos, noticias y recursos actualizados para mantenerte informado.</p>
  </section>

  <!-- FEATURED POST (dynamic) -->
  <section data-blog="featured-post" data-sitio-id="{{SITIO_ID}}" style="padding:50px 20px;background:#0f172a;color:white;border-radius:0;">
    <div data-blog-item style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1.1fr .9fr;gap:35px;align-items:center;">
      <div>
        <span data-blog-category style="display:inline-block;padding:7px 14px;background:#2563eb;border-radius:999px;font-size:13px;font-weight:700;margin-bottom:18px;">Destacado</span>
        <h2 data-blog-title style="font-size:38px;line-height:1.15;margin:0 0 16px 0;">Artículo destacado del blog</h2>
        <p data-blog-excerpt style="font-size:16px;line-height:1.7;color:#cbd5e1;margin:0 0 24px 0;">
          Este bloque muestra la publicación principal del blog, ideal para destacar el contenido más importante.
        </p>
        <a data-blog-link href="#" style="display:inline-block;padding:13px 22px;background:white;color:#0f172a;border-radius:10px;text-decoration:none;font-weight:700;">Leer artículo</a>
      </div>
      <img data-blog-image src="https://placehold.co/800x520/334155/ffffff?text=Post+Destacado" alt="Post destacado" style="width:100%;height:360px;object-fit:cover;border-radius:16px;">
    </div>
    <div data-blog-empty style="display:none;text-align:center;padding:30px;color:#cbd5e1;">
      No hay artículo destacado disponible.
    </div>
  </section>

  <!-- SEARCH -->
  <section data-blog="search" style="padding:30px 20px;background:white;border-bottom:1px solid #e2e8f0;">
    <div style="max-width:600px;margin:0 auto;text-align:center;">
      <form data-blog-search-form style="display:flex;gap:10px;">
        <input data-blog-search-input type="text" placeholder="Buscar artículos..." style="flex:1;padding:12px 16px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
        <button type="submit" style="padding:12px 24px;background:#2563eb;color:white;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">Buscar</button>
      </form>
    </div>
  </section>

  <!-- BLOG GRID (dynamic) -->
  <section data-blog="posts-grid" data-sitio-id="{{SITIO_ID}}" data-limit="6" style="padding:60px 20px;background:#f8fafc;">
    <div style="max-width:1100px;margin:0 auto;">
      <div style="text-align:center;margin-bottom:35px;">
        <h2 style="font-size:34px;margin:0 0 10px 0;color:#0f172a;">Artículos Recientes</h2>
        <p style="font-size:16px;color:#64748b;margin:0;">Contenido actualizado desde nuestro blog.</p>
      </div>
      <div data-blog-list style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;">
        <article data-blog-item style="background:white;border-radius:14px;overflow:hidden;box-shadow:0 10px 25px rgba(15,23,42,.08);">
          <img data-blog-image src="https://placehold.co/700x420/e2e8f0/334155?text=Blog" alt="Imagen del post" style="width:100%;height:190px;object-fit:cover;">
          <div style="padding:22px;">
            <span data-blog-category style="display:inline-block;font-size:12px;color:#2563eb;font-weight:700;margin-bottom:10px;">Categoría</span>
            <h3 data-blog-title style="font-size:20px;margin:0 0 10px 0;color:#0f172a;">Título del artículo</h3>
            <p data-blog-excerpt style="font-size:14px;color:#64748b;line-height:1.6;margin:0 0 18px 0;">Resumen breve del artículo para mostrar una vista previa del contenido.</p>
            <a data-blog-link href="#" style="color:#2563eb;font-weight:700;text-decoration:none;">Leer más →</a>
          </div>
        </article>
        <article data-blog-item style="background:white;border-radius:14px;overflow:hidden;box-shadow:0 10px 25px rgba(15,23,42,.08);">
          <img data-blog-image src="https://placehold.co/700x420/dbeafe/1e40af?text=Post" alt="Imagen del post" style="width:100%;height:190px;object-fit:cover;">
          <div style="padding:22px;">
            <span data-blog-category style="display:inline-block;font-size:12px;color:#2563eb;font-weight:700;margin-bottom:10px;">Noticias</span>
            <h3 data-blog-title style="font-size:20px;margin:0 0 10px 0;color:#0f172a;">Segundo artículo</h3>
            <p data-blog-excerpt style="font-size:14px;color:#64748b;line-height:1.6;margin:0 0 18px 0;">Este es un ejemplo visual que luego será reemplazado por datos reales.</p>
            <a data-blog-link href="#" style="color:#2563eb;font-weight:700;text-decoration:none;">Leer más →</a>
          </div>
        </article>
        <article data-blog-item style="background:white;border-radius:14px;overflow:hidden;box-shadow:0 10px 25px rgba(15,23,42,.08);">
          <img data-blog-image src="https://placehold.co/700x420/fef3c7/92400e?text=Articulo" alt="Imagen del post" style="width:100%;height:190px;object-fit:cover;">
          <div style="padding:22px;">
            <span data-blog-category style="display:inline-block;font-size:12px;color:#2563eb;font-weight:700;margin-bottom:10px;">Actualidad</span>
            <h3 data-blog-title style="font-size:20px;margin:0 0 10px 0;color:#0f172a;">Tercer artículo</h3>
            <p data-blog-excerpt style="font-size:14px;color:#64748b;line-height:1.6;margin:0 0 18px 0;">Vista previa para representar cómo se verán los posts publicados.</p>
            <a data-blog-link href="#" style="color:#2563eb;font-weight:700;text-decoration:none;">Leer más →</a>
          </div>
        </article>
      </div>
      <div data-blog-empty style="display:none;text-align:center;padding:30px;color:#64748b;">
        No hay artículos publicados todavía.
      </div>
    </div>
  </section>

  <!-- CATEGORIES (example static) -->
  <section style="padding:40px 20px;background:white;text-align:center;">
    <h3 style="font-size:20px;margin:0 0 20px 0;color:#0f172a;">Categorías</h3>
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;">
      <span style="padding:8px 20px;background:#e0e7ff;color:#2563eb;border-radius:999px;font-size:14px;font-weight:600;">General</span>
      <span style="padding:8px 20px;background:#e0e7ff;color:#2563eb;border-radius:999px;font-size:14px;font-weight:600;">Tecnología</span>
      <span style="padding:8px 20px;background:#e0e7ff;color:#2563eb;border-radius:999px;font-size:14px;font-weight:600;">Consejos</span>
    </div>
  </section>

  <!-- FOOTER -->
  <footer style="padding:40px 20px;background:#0f172a;color:white;">
    <div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:30px;">
      <div>
        <strong style="font-size:18px;display:block;margin-bottom:12px;color:#2563eb;">Blog News</strong>
        <p style="font-size:13px;opacity:0.7;">Tu fuente de información actualizada y contenido de calidad.</p>
      </div>
      <div>
        <strong style="font-size:14px;display:block;margin-bottom:12px;">Enlaces</strong>
        <div style="display:flex;flex-direction:column;gap:6px;font-size:13px;">
          <a href="#" style="color:white;opacity:0.7;text-decoration:none;">Inicio</a>
          <a href="#" style="color:white;opacity:0.7;text-decoration:none;">Blog</a>
          <a href="#" style="color:white;opacity:0.7;text-decoration:none;">Contacto</a>
        </div>
      </div>
      <div>
        <strong style="font-size:14px;display:block;margin-bottom:12px;">Síguenos</strong>
        <div style="display:flex;gap:12px;font-size:20px;">
          <i class="fa fa-facebook" style="opacity:0.7;cursor:pointer;"></i>
          <i class="fa fa-twitter" style="opacity:0.7;cursor:pointer;"></i>
          <i class="fa fa-instagram" style="opacity:0.7;cursor:pointer;"></i>
        </div>
      </div>
    </div>
    <div style="text-align:center;border-top:1px solid #1e293b;padding-top:20px;margin-top:30px;font-size:13px;opacity:0.6;">
      &copy; 2026 Blog News. Todos los derechos reservados.
    </div>
  </footer>

</body>
</html>"""


TIENDA_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mi Tienda Online</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}
  </style>
</head>
<body>

  <!-- NAVBAR -->
  <header style="padding:15px 40px;display:flex;align-items:center;justify-content:space-between;background:#0f172a;color:white;position:sticky;top:0;z-index:100;">
    <div style="font-size:22px;font-weight:700;color:#f59e0b;">Mi Tienda</div>
    <nav style="display:flex;gap:25px;">
      <a href="#" style="color:white;text-decoration:none;font-size:14px;">Inicio</a>
      <a href="#productos" style="color:white;text-decoration:none;font-size:14px;">Productos</a>
      <a href="#carrito" style="color:white;text-decoration:none;font-size:14px;">Carrito</a>
      <a href="#checkout" style="color:white;text-decoration:none;font-size:14px;">Checkout</a>
    </nav>
  </header>

  <!-- HERO -->
  <section style="padding:80px 20px;background:linear-gradient(135deg,#0f172a,#1e293b);text-align:center;color:white;">
    <h1 style="font-size:44px;font-weight:700;margin:0 0 16px 0;">Bienvenido a <span style="color:#f59e0b;">Mi Tienda</span></h1>
    <p style="font-size:18px;opacity:0.85;max-width:500px;margin:0 auto 30px;">Descubre los mejores productos con los mejores precios. Envíos a todo el país.</p>
    <a href="#productos" style="display:inline-block;padding:14px 32px;background:#f59e0b;color:#0f172a;border-radius:8px;text-decoration:none;font-weight:700;">Ver productos</a>
  </section>

  <!-- CATEGORÍAS (dynamic) -->
  <section data-tienda="categories" data-sitio-id="{{SITIO_ID}}" style="padding:40px 20px;background:white;">
    <div style="max-width:900px;margin:0 auto;text-align:center;">
      <h3 style="font-size:20px;margin:0 0 18px 0;color:#0f172a;">Categorías</h3>
      <div data-tienda-list style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;">
        <button data-tienda-item data-categoria-id="" style="padding:10px 22px;background:#f1f5f9;color:#0f172a;border:none;border-radius:999px;font-size:14px;font-weight:600;cursor:pointer;">
          <span data-tienda-category-name>Todas</span>
        </button>
        <button data-tienda-item data-categoria-id="0" style="padding:10px 22px;background:#f1f5f9;color:#0f172a;border:none;border-radius:999px;font-size:14px;font-weight:600;cursor:pointer;">
          <span data-tienda-category-name>Electrónicos</span>
        </button>
        <button data-tienda-item data-categoria-id="0" style="padding:10px 22px;background:#f1f5f9;color:#0f172a;border:none;border-radius:999px;font-size:14px;font-weight:600;cursor:pointer;">
          <span data-tienda-category-name>Ropa</span>
        </button>
        <button data-tienda-item data-categoria-id="0" style="padding:10px 22px;background:#f1f5f9;color:#0f172a;border:none;border-radius:999px;font-size:14px;font-weight:600;cursor:pointer;">
          <span data-tienda-category-name>Hogar</span>
        </button>
      </div>
      <div data-tienda-empty style="display:none;padding:20px;color:#64748b;">
        No hay categorías disponibles.
      </div>
    </div>
  </section>

  <!-- PRODUCTO DESTACADO (dynamic) -->
  <section data-tienda="featured-product" data-sitio-id="{{SITIO_ID}}" style="padding:50px 20px;">
    <div style="max-width:1000px;margin:0 auto;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);border-radius:24px;overflow:hidden;position:relative;">
      <span style="position:absolute;top:20px;left:20px;background:#f59e0b;color:#0f172a;font-size:12px;font-weight:800;padding:6px 14px;border-radius:999px;text-transform:uppercase;letter-spacing:1px;z-index:2;">Destacado</span>
      <div data-tienda-item style="display:flex;flex-wrap:wrap;align-items:center;gap:0;">
        <div style="flex:1;min-width:300px;padding:50px 40px;">
          <h2 data-tienda-product-name style="font-size:34px;margin:0 0 12px 0;color:white;line-height:1.1;">Producto destacado</h2>
          <p data-tienda-product-desc style="font-size:15px;color:#94a3b8;line-height:1.7;margin:0 0 20px 0;">Nuestro producto estrella con la mejor relación calidad-precio.</p>
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;">
            <span data-tienda-product-price style="font-size:30px;font-weight:800;color:white;">S/ 199.90</span>
            <span data-tienda-product-compare style="display:none;font-size:15px;color:#64748b;text-decoration:line-through;">S/ 249.90</span>
          </div>
          <button data-tienda-add-cart style="padding:14px 32px;background:#f59e0b;color:#0f172a;border:none;border-radius:10px;font-size:16px;font-weight:800;cursor:pointer;">Agregar al carrito</button>
        </div>
        <div style="flex:1;min-width:280px;height:350px;overflow:hidden;">
          <img data-tienda-product-image src="https://placehold.co/600x500/f59e0b/0f172a?text=Destacado" alt="Producto destacado" style="width:100%;height:100%;object-fit:cover;display:block;">
        </div>
      </div>
      <div data-tienda-empty style="display:none;text-align:center;padding:40px;color:#94a3b8;">
        No hay producto destacado disponible.
      </div>
    </div>
  </section>

  <!-- PRODUCTOS GRID (dynamic) -->
  <section id="productos" data-tienda="products-grid" data-sitio-id="{{SITIO_ID}}" data-limit="6" style="padding:60px 20px;background:#f8fafc;">
    <div style="max-width:1100px;margin:0 auto;">
      <div style="text-align:center;margin-bottom:35px;">
        <h2 style="font-size:34px;margin:0 0 10px 0;color:#0f172a;">Nuestros Productos</h2>
        <p style="font-size:16px;color:#64748b;margin:0;">Descubre nuestra selección de productos.</p>
      </div>
      <div data-tienda-list style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;">
        <article data-tienda-item style="background:white;border-radius:14px;overflow:hidden;box-shadow:0 10px 25px rgba(15,23,42,.08);position:relative;">
          <span data-tienda-badge-discount style="display:none;position:absolute;top:12px;left:12px;background:#ef4444;color:white;font-size:11px;font-weight:700;padding:4px 10px;border-radius:999px;z-index:1;">-20%</span>
          <img data-tienda-product-image src="https://placehold.co/700x420/e2e8f0/334155?text=Producto" alt="Producto" style="width:100%;height:190px;object-fit:cover;">
          <div style="padding:20px;">
            <h3 data-tienda-product-name style="font-size:18px;margin:0 0 6px 0;color:#0f172a;">Producto</h3>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
              <span data-tienda-product-price style="font-size:22px;font-weight:800;color:#0f172a;">S/ 99.90</span>
              <span data-tienda-product-compare style="display:none;font-size:14px;color:#94a3b8;text-decoration:line-through;">S/ 129.90</span>
            </div>
            <button data-tienda-add-cart style="width:100%;padding:10px;background:#0f172a;color:white;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;">Agregar al carrito</button>
          </div>
        </article>
        <article data-tienda-item style="background:white;border-radius:14px;overflow:hidden;box-shadow:0 10px 25px rgba(15,23,42,.08);position:relative;">
          <span data-tienda-badge-discount style="display:none;position:absolute;top:12px;left:12px;background:#ef4444;color:white;font-size:11px;font-weight:700;padding:4px 10px;border-radius:999px;z-index:1;">-20%</span>
          <img data-tienda-product-image src="https://placehold.co/700x420/dbeafe/1e40af?text=Prod+2" alt="Producto" style="width:100%;height:190px;object-fit:cover;">
          <div style="padding:20px;">
            <h3 data-tienda-product-name style="font-size:18px;margin:0 0 6px 0;color:#0f172a;">Producto 2</h3>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
              <span data-tienda-product-price style="font-size:22px;font-weight:800;color:#0f172a;">S/ 149.90</span>
              <span data-tienda-product-compare style="display:none;font-size:14px;color:#94a3b8;text-decoration:line-through;">S/ 179.90</span>
            </div>
            <button data-tienda-add-cart style="width:100%;padding:10px;background:#0f172a;color:white;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;">Agregar al carrito</button>
          </div>
        </article>
        <article data-tienda-item style="background:white;border-radius:14px;overflow:hidden;box-shadow:0 10px 25px rgba(15,23,42,.08);position:relative;">
          <span data-tienda-badge-discount style="display:none;position:absolute;top:12px;left:12px;background:#ef4444;color:white;font-size:11px;font-weight:700;padding:4px 10px;border-radius:999px;z-index:1;">-10%</span>
          <img data-tienda-product-image src="https://placehold.co/700x420/fef3c7/92400e?text=Prod+3" alt="Producto" style="width:100%;height:190px;object-fit:cover;">
          <div style="padding:20px;">
            <h3 data-tienda-product-name style="font-size:18px;margin:0 0 6px 0;color:#0f172a;">Producto 3</h3>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
              <span data-tienda-product-price style="font-size:22px;font-weight:800;color:#0f172a;">S/ 79.90</span>
              <span data-tienda-product-compare style="display:none;font-size:14px;color:#94a3b8;text-decoration:line-through;">S/ 89.90</span>
            </div>
            <button data-tienda-add-cart style="width:100%;padding:10px;background:#0f172a;color:white;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;">Agregar al carrito</button>
          </div>
        </article>
      </div>
      <div data-tienda-empty style="display:none;text-align:center;padding:30px;color:#64748b;">
        No hay productos disponibles todavía.
      </div>
    </div>
  </section>

  <!-- CARRITO (dynamic) -->
  <section id="carrito" data-tienda="cart" data-sitio-id="{{SITIO_ID}}" style="padding:60px 20px;background:white;">
    <div style="max-width:900px;margin:0 auto;">
      <h2 style="font-size:28px;margin:0 0 24px 0;color:#0f172a;">Carrito de Compras</h2>
      <div data-tienda-list>
        <div data-tienda-item data-tienda-item-id="" style="display:flex;align-items:center;gap:16px;padding:16px;background:#f8fafc;border-radius:12px;margin-bottom:12px;">
          <img data-tienda-product-image src="https://placehold.co/64x64/e2e8f0/334155?text=P" alt="Producto" style="width:64px;height:64px;object-fit:cover;border-radius:10px;flex-shrink:0;">
          <div style="flex:1;min-width:0;">
            <h4 data-tienda-product-name style="font-size:15px;margin:0 0 4px 0;color:#0f172a;">Producto</h4>
            <span data-tienda-product-price style="font-size:14px;font-weight:700;color:#0f172a;">S/ 99.90</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;border:1px solid #e2e8f0;border-radius:6px;overflow:hidden;">
            <button data-tienda-qty-minus style="width:32px;height:32px;border:none;background:#f8fafc;font-size:16px;cursor:pointer;color:#0f172a;font-weight:700;">−</button>
            <span data-tienda-qty-value style="width:36px;text-align:center;font-size:14px;font-weight:600;color:#0f172a;">1</span>
            <button data-tienda-qty-plus style="width:32px;height:32px;border:none;background:#f8fafc;font-size:16px;cursor:pointer;color:#0f172a;font-weight:700;">+</button>
          </div>
          <span data-tienda-item-subtotal style="font-size:15px;font-weight:700;color:#0f172a;min-width:70px;text-align:right;">S/ 99.90</span>
          <button data-tienda-item-remove style="background:none;border:none;font-size:22px;color:#ef4444;cursor:pointer;padding:4px;">×</button>
        </div>
      </div>
      <div style="text-align:right;padding:20px 0;border-top:2px solid #e2e8f0;margin-top:16px;">
        <div style="font-size:18px;color:#64748b;margin-bottom:8px;">
          Total: <span data-tienda-cart-total style="font-size:28px;font-weight:800;color:#0f172a;margin-left:12px;">S/ 0.00</span>
        </div>
      </div>
      <div data-tienda-empty style="display:none;text-align:center;padding:40px;color:#64748b;">
        Tu carrito está vacío.
      </div>
    </div>
  </section>

  <!-- CHECKOUT (dynamic) -->
  <section id="checkout" data-tienda="checkout" data-sitio-id="{{SITIO_ID}}" style="padding:60px 20px;background:#f8fafc;">
    <div style="max-width:700px;margin:0 auto;">
      <h2 style="font-size:28px;margin:0 0 24px 0;color:#0f172a;">Finalizar Compra</h2>
      <form data-tienda-checkout-form>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
          <div style="grid-column:1/-1;">
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Nombre completo</label>
            <input data-tienda-field-nombre type="text" required style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
          </div>
          <div>
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Email</label>
            <input data-tienda-field-email type="email" required style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
          </div>
          <div>
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Teléfono</label>
            <input data-tienda-field-telefono type="tel" style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
          </div>
          <div style="grid-column:1/-1;">
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Dirección de envío</label>
            <input data-tienda-field-direccion type="text" style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
          </div>
          <div>
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Ciudad</label>
            <input data-tienda-field-ciudad type="text" style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
          </div>
          <div>
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">País</label>
            <input data-tienda-field-pais type="text" style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
          </div>
          <div>
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Código postal</label>
            <input data-tienda-field-codigo-postal type="text" style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;">
          </div>
          <div>
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Método de pago</label>
            <select data-tienda-field-metodo-pago style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;background:white;">
              <option value="efectivo">Efectivo</option>
              <option value="tarjeta">Tarjeta de crédito/débito</option>
              <option value="transferencia">Transferencia bancaria</option>
              <option value="yape">Yape / Plin</option>
            </select>
          </div>
          <div style="grid-column:1/-1;">
            <label style="display:block;font-size:14px;font-weight:600;color:#0f172a;margin-bottom:6px;">Notas del pedido</label>
            <textarea data-tienda-field-notas rows="3" style="width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:15px;outline:none;resize:vertical;"></textarea>
          </div>
        </div>
        <button type="submit" style="width:100%;padding:16px;background:#0f172a;color:white;border:none;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer;">Confirmar Pedido</button>
      </form>
      <div data-tienda-checkout-success style="display:none;text-align:center;padding:40px;background:#f0fdf4;border-radius:12px;margin-top:20px;">
        <span style="font-size:48px;">&#10003;</span>
        <h3 style="color:#16a34a;margin:10px 0;">Pedido Confirmado</h3>
        <p data-tienda-checkout-message style="color:#166534;">Gracias por tu compra. Te contactaremos pronto.</p>
      </div>
      <div data-tienda-checkout-error style="display:none;text-align:center;padding:20px;background:#fef2f2;border-radius:12px;margin-top:20px;color:#dc2626;"></div>
    </div>
  </section>

  <!-- FOOTER -->
  <footer style="padding:40px 20px;background:#0f172a;color:white;">
    <div style="max-width:1100px;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:30px;">
      <div>
        <strong style="font-size:18px;display:block;margin-bottom:12px;color:#f59e0b;">Mi Tienda</strong>
        <p style="font-size:13px;opacity:0.7;">Tu tienda online de confianza. Productos de calidad, mejores precios.</p>
      </div>
      <div>
        <strong style="font-size:14px;display:block;margin-bottom:12px;">Enlaces</strong>
        <div style="display:flex;flex-direction:column;gap:6px;font-size:13px;">
          <a href="#" style="color:white;opacity:0.7;text-decoration:none;">Inicio</a>
          <a href="#productos" style="color:white;opacity:0.7;text-decoration:none;">Productos</a>
          <a href="#carrito" style="color:white;opacity:0.7;text-decoration:none;">Carrito</a>
        </div>
      </div>
      <div>
        <strong style="font-size:14px;display:block;margin-bottom:12px;">Contacto</strong>
        <div style="display:flex;flex-direction:column;gap:6px;font-size:13px;opacity:0.7;">
          <span>+51 999 888 777</span>
          <span>ventas@mitienda.pe</span>
          <span>Lima, Perú</span>
        </div>
      </div>
    </div>
    <div style="text-align:center;border-top:1px solid #1e293b;padding-top:20px;margin-top:30px;font-size:13px;opacity:0.6;">
      &copy; 2026 Mi Tienda Online. Todos los derechos reservados.
    </div>
  </footer>

</body>
</html>"""


if __name__ == "__main__":
    seed_sitios()
