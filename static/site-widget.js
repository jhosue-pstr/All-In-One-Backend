(function(){var v="/api";function C(){try{return localStorage.getItem("site_token")}catch{return null}}function k(t){try{localStorage.setItem("site_token",t)}catch{}}function A(){try{localStorage.removeItem("site_token")}catch{}}async function u(t,e={}){const o=C(),n={"Content-Type":"application/json",...o?{Authorization:`Bearer ${o}`}:{},...e.headers||{}},r=await fetch(`${v}${t}`,{...e,headers:n});if(!r.ok){const i=await r.json().catch(()=>({detail:"Error en la solicitud"}));throw new Error(i.detail||"Error en la solicitud")}return r.status===204?{}:r.json()}async function m(t){try{const e=await u("/site-auth/me"),o=t.querySelector('[data-perfil="nombre_completo"]');o&&(o.textContent=`${e.nombre} ${e.apellido}`);const n=t.querySelector('[data-perfil="correo"]');n&&(n.textContent=e.correo);const r=t.querySelector('[data-perfil="avatar"]');r&&(r.src=`https://placehold.co/80x80/667eea/ffffff?text=${(e.nombre?.charAt(0)||"U").toUpperCase()}`)}catch{const e=document.querySelector('[data-auth="login"]');e&&(e.style.display=""),t.style.display="none"}}function h(t){const e=t.closest("[data-sitio-id]")?.getAttribute("data-sitio-id");return e?Number(e):null}function d(t,e){const o=t.querySelector(".auth-error");o&&(o.textContent=e,o.style.display="block")}function b(t){const e=t.querySelector(".auth-error");e&&(e.style.display="none")}function I(t){t.addEventListener("submit",async e=>{e.preventDefault(),b(t);const o=h(t);if(!o){d(t,"Error: sitio no identificado");return}const n=new FormData(t),r=n.get("correo"),i=n.get("contrasena");if(!r||!i){d(t,"Todos los campos son obligatorios");return}const a=t.querySelector('button[type="submit"]');a&&(a.disabled=!0,a.textContent="Entrando...");try{k((await u("/site-auth/login",{method:"POST",body:JSON.stringify({correo:r,contrasena:i,id_sitio:o})})).access_token);const l=t.closest("[data-auth]");l&&(l.style.display="none");const c=document.querySelector('[data-auth="perfil"]');c&&(c.style.display="",m(c))}catch(l){d(t,l instanceof Error?l.message:"Error al iniciar sesión")}finally{a&&(a.disabled=!1,a.textContent="Entrar")}})}function L(t){t.addEventListener("submit",async e=>{e.preventDefault(),b(t);const o=h(t);if(!o){d(t,"Error: sitio no identificado");return}const n=new FormData(t),r=n.get("nombre"),i=n.get("apellido"),a=n.get("correo"),l=n.get("contrasena");if(!r||!i||!a||!l){d(t,"Todos los campos son obligatorios");return}const c=t.querySelector('button[type="submit"]');c&&(c.disabled=!0,c.textContent="Registrando...");try{await u("/site-auth/registro",{method:"POST",body:JSON.stringify({nombre:r,apellido:i,correo:a,contrasena:l,id_sitio:o})}),t.innerHTML=`
        <div style="text-align:center;padding:20px;">
          <p style="color:#27ae60;font-size:18px;font-weight:600;">¡Registro exitoso!</p>
          <p style="color:#666;">Ahora puedes iniciar sesión.</p>
          <button type="button" style="padding:12px 24px;background:#667eea;color:white;border:none;border-radius:6px;font-size:16px;cursor:pointer;" onclick="window.location.reload()">
            Iniciar Sesión
          </button>
        </div>
      `}catch(y){d(t,y instanceof Error?y.message:"Error al registrarse")}finally{c&&(c.disabled=!1,c.textContent="Registrarse")}})}function _(t){t.addEventListener("click",async()=>{try{await u("/site-auth/logout",{method:"POST"})}catch{}A(),window.location.reload()})}var S="/api";function p(t){const e=t.getAttribute("data-sitio-id");if(!e||e==="{{SITIO_ID}}"){const n=document.body.getAttribute("data-sitio-id");if(!n)return null;const r=Number(n);return Number.isNaN(r)?null:r}const o=Number(e);return Number.isNaN(o)?null:o}function B(t,e){const o=t.getAttribute("data-limit");if(!o)return e;const n=Number(o);return Number.isNaN(n)?e:n}function x(t){if(!t)return"Publicado recientemente";try{return new Intl.DateTimeFormat("es-PE",{day:"2-digit",month:"long",year:"numeric"}).format(new Date(t))}catch{return"Publicado recientemente"}}function q(t){return t?(t.startsWith("http"),t):"https://placehold.co/700x420/e2e8f0/334155?text=Blog"}function N(t){return`${window.location.pathname.replace(/\/$/,"")}?post=${encodeURIComponent(t.slug)}`}async function E(t){const e=await fetch(`${S}/modules/blog/${t}/posts?only_published=true`);if(!e.ok)throw new Error("No se pudieron cargar los posts del blog");return e.json()}async function T(t,e){const o=await fetch(`${S}/modules/blog/${t}/posts/${encodeURIComponent(e)}`);if(!o.ok)throw new Error("No se pudo cargar el post");return o.json()}function s(t){const e=t.querySelector("[data-blog-list]"),o=t.querySelector("[data-blog-item]"),n=t.querySelector("[data-blog-empty]");e&&(e.innerHTML=""),o&&(o.style.display="none"),n&&(n.style.display="block")}function g(t,e){const o=t.querySelector("[data-blog-image]"),n=t.querySelector("[data-blog-title]"),r=t.querySelector("[data-blog-excerpt]"),i=t.querySelector("[data-blog-content]"),a=t.querySelector("[data-blog-date]"),l=t.querySelector("[data-blog-link]"),c=t.querySelector("[data-blog-category]");o&&(o.src=q(e.featured_image),o.alt=e.title),n&&(n.textContent=e.title),r&&(r.textContent=e.excerpt||e.meta_description||e.content.replace(/<[^>]*>/g,"").slice(0,150)+"..."),i&&(i.innerHTML=e.content),a&&(a.textContent=x(e.published_at||e.created_at)),l&&(l.href=N(e)),c&&(c.textContent="Blog")}function P(t,e){const o=t.querySelector("[data-blog-list]"),n=t.querySelector("[data-blog-item]"),r=t.querySelector("[data-blog-empty]");if(!o||!n)return;if(!e.length){s(t);return}r&&(r.style.display="none");const i=n.cloneNode(!0);o.innerHTML="",e.forEach(a=>{const l=i.cloneNode(!0);l.style.display="",l.style.cursor="pointer",g(l,a),l.addEventListener("click",c=>{c.preventDefault(),w(a)}),o.appendChild(l)})}async function f(t,e){const o=p(t);if(!o){s(t);return}try{const n=B(t,e);P(t,(await E(o)).slice(0,n))}catch(n){console.error("[Blog Widget]",n),s(t)}}async function D(t){const e=p(t);if(!e){s(t);return}try{const o=(await E(e))[0];if(!o){s(t);return}const n=t.querySelector("[data-blog-item]")||t;g(n,o),n.style.cursor="pointer",n.addEventListener("click",i=>{i.preventDefault(),w(o)});const r=t.querySelector("[data-blog-empty]");r&&(r.style.display="none")}catch(o){console.error("[Blog Widget]",o),s(t)}}async function $(t){const e=p(t),o=new URLSearchParams(window.location.search).get("post");if(!(!e||!o))try{const n=await T(e,o);g(t,n),n.meta_title&&(document.title=n.meta_title);const r=n.meta_description||n.excerpt;if(r){let a=document.querySelector('meta[name="description"]');a||(a=document.createElement("meta"),a.name="description",document.head.appendChild(a)),a.content=r}const i=t.querySelector("[data-blog-empty]");i&&(i.style.display="none")}catch(n){console.error("[Blog Widget]",n),s(t)}}function z(t){const e=t.querySelector("[data-blog-search-form]"),o=t.querySelector("[data-blog-search-input]");!e||!o||e.addEventListener("submit",n=>{n.preventDefault();const r=o.value.trim().toLowerCase();document.querySelectorAll('[data-blog="posts-grid"], [data-blog="posts-list"], [data-blog="recent-posts"]').forEach(i=>{i.querySelectorAll("[data-blog-item]").forEach(a=>{const l=a.querySelector("[data-blog-title]")?.textContent?.toLowerCase()||"",c=a.querySelector("[data-blog-excerpt]")?.textContent?.toLowerCase()||"",y=!r||l.includes(r)||c.includes(r);a.style.display=y?"":"none"})})})}function M(){let t=document.getElementById("blog-post-modal");return t||(t=document.createElement("div"),t.id="blog-post-modal",t.style.cssText=`
    position: fixed;
    inset: 0;
    z-index: 99999;
    background: rgba(15, 23, 42, 0.78);
    display: none;
    align-items: center;
    justify-content: center;
    padding: 24px;
  `,t.innerHTML=`
    <div data-blog-modal-card style="
      width: min(960px, 100%);
      max-height: 90vh;
      overflow: auto;
      background: white;
      border-radius: 22px;
      box-shadow: 0 25px 80px rgba(0,0,0,.35);
      position: relative;
    ">
      <button data-blog-modal-close style="
        position:absolute;
        top:14px;
        right:14px;
        width:42px;
        height:42px;
        border:none;
        border-radius:999px;
        background:rgba(15,23,42,.85);
        color:white;
        font-size:26px;
        cursor:pointer;
        z-index:2;
      ">×</button>

      <img data-blog-modal-image src="" alt="" style="
        width:100%;
        height:420px;
        object-fit:cover;
        display:block;
      ">

      <div style="padding:30px;">
        <span data-blog-modal-category style="
          display:inline-block;
          color:#2563eb;
          font-size:14px;
          font-weight:800;
          margin-bottom:12px;
        ">Blog</span>

        <h2 data-blog-modal-title style="
          margin:0 0 10px;
          color:#0f172a;
          font-size:36px;
          line-height:1.15;
        "></h2>

        <p data-blog-modal-date style="
          margin:0 0 20px;
          color:#64748b;
          font-size:14px;
        "></p>

        <p data-blog-modal-excerpt style="
          margin:0 0 24px;
          color:#475569;
          font-size:17px;
          line-height:1.7;
          font-weight:600;
        "></p>

        <div data-blog-modal-content style="
          color:#334155;
          font-size:17px;
          line-height:1.8;
        "></div>
      </div>
    </div>
  `,document.body.appendChild(t),t.querySelector("[data-blog-modal-close]")?.addEventListener("click",()=>{t.style.display="none",document.body.style.overflow=""}),t.addEventListener("click",e=>{e.target===t&&(t.style.display="none",document.body.style.overflow="")}),document.addEventListener("keydown",e=>{e.key==="Escape"&&t.style.display!=="none"&&(t.style.display="none",document.body.style.overflow="")}),t)}function w(t){const e=M(),o=e.querySelector("[data-blog-modal-image]"),n=e.querySelector("[data-blog-modal-title]"),r=e.querySelector("[data-blog-modal-date]"),i=e.querySelector("[data-blog-modal-excerpt]"),a=e.querySelector("[data-blog-modal-content]");o&&(o.src=q(t.featured_image),o.alt=t.title),n&&(n.textContent=t.title),r&&(r.textContent=x(t.published_at||t.created_at)),i&&(i.textContent=t.excerpt||t.meta_description||""),a&&(a.innerHTML=t.content||""),e.style.display="flex",document.body.style.overflow="hidden"}function j(){document.querySelectorAll('[data-blog="posts-grid"]').forEach(t=>{f(t,6)}),document.querySelectorAll('[data-blog="posts-list"]').forEach(t=>{f(t,8)}),document.querySelectorAll('[data-blog="recent-posts"]').forEach(t=>{f(t,5)}),document.querySelectorAll('[data-blog="featured-post"]').forEach(t=>{D(t)}),document.querySelectorAll('[data-blog="post-detail"]').forEach(t=>{$(t)}),document.querySelectorAll('[data-blog="search"]').forEach(t=>{z(t)})}(()=>{function t(){document.querySelectorAll('[data-auth="login"] form').forEach(I),document.querySelectorAll('[data-auth="registro"] form').forEach(L),document.querySelectorAll('[data-auth="logout"]').forEach(_),document.querySelectorAll('[data-auth="perfil"]').forEach(e=>{try{localStorage.getItem("site_token")?(e.style.display="",m(e)):e.style.display="none"}catch{e.style.display="none"}}),document.querySelectorAll('[data-auth="login"]').forEach(e=>{try{localStorage.getItem("site_token")&&(e.style.display="none")}catch{}}),j()}document.readyState==="loading"?document.addEventListener("DOMContentLoaded",t):t()})()})();
