/* Service worker PG del Campo - version corregida
   Estrategia:
   - Paginas HTML (navegacion): RED PRIMERO. Si hay internet, siempre trae la
     version fresca (nunca sirve una pagina en blanco cacheada). Si no hay
     internet, cae al cache.
   - Recursos estaticos (vendor/, imagenes, css, js): CACHE PRIMERO, con
     actualizacion en segundo plano.
   - CACHE_VERSION versionado: al cambiar el numero se borran los caches viejos
     automaticamente en la siguiente carga.
*/
const CACHE_VERSION = 'pg-campo-v3';
const STATIC_CACHE  = CACHE_VERSION + '-static';
const PAGES_CACHE   = CACHE_VERSION + '-pages';

// Recursos que conviene precachear (ajusta si agregas/quitas librerias).
const PRECACHE = [
  './',
  './index.html',
  './panel.html',
  './tienda.html',
  './tarjeta-fidelidad.html',
  './vendor/tailwind.js',
  './vendor/chart.umd.min.js',
  './vendor/qrcode.min.js',
  './vendor/fontawesome/css/all.min.css',
  './vendor/fonts/fonts.css'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) =>
      // addAll falla si UN recurso da 404; usamos add individual tolerante
      Promise.all(PRECACHE.map((url) =>
        cache.add(url).catch(() => { /* ignorar recursos faltantes */ })
      ))
    )
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== PAGES_CACHE)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  // No interceptar Firebase / dominios externos: dejar pasar a la red.
  if (url.origin !== self.location.origin) return;

  const isPage =
    req.mode === 'navigate' ||
    (req.headers.get('accept') || '').includes('text/html');

  if (isPage) {
    // RED PRIMERO para paginas: evita servir HTML en blanco cacheado.
    event.respondWith(
      fetch(req)
        .then((resp) => {
          const copy = resp.clone();
          caches.open(PAGES_CACHE).then((c) => c.put(req, copy));
          return resp;
        })
        .catch(() =>
          caches.match(req).then((c) => c || caches.match('./index.html'))
        )
    );
    return;
  }

  // CACHE PRIMERO para estaticos (vendor, imagenes, etc.)
  event.respondWith(
    caches.match(req).then((cached) => {
      const network = fetch(req)
        .then((resp) => {
          if (resp && resp.status === 200) {
            const copy = resp.clone();
            caches.open(STATIC_CACHE).then((c) => c.put(req, copy));
          }
          return resp;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
