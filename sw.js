/* ===========================================================
   Service Worker - PG del Campo (Tarjeta de Fidelidad)
   Estrategia:
   - Navegación (index.html): RED PRIMERO  -> siempre intenta traer
     la versión nueva; si no hay internet, usa la copia guardada.
   - Recursos (css/js/img): STALE-WHILE-REVALIDATE -> muestra rápido
     lo guardado y actualiza en segundo plano.
   - En cada publicación sube el número de CACHE_VERSION: eso borra
     la caché vieja y obliga a los teléfonos a tomar lo nuevo.
   =========================================================== */

/* 👇 IMPORTANTE: sube este número (v1 -> v2 -> v3...) cada vez que
   publiques cambios en la tarjeta. Es lo único que debes tocar. */
const CACHE_VERSION = 'pg-tarjeta-v4';

/* Archivos base para que la app abra incluso sin conexión. */
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.webmanifest'
];

/* ---------- INSTALACIÓN: guarda los archivos base ---------- */
self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(function (cache) {
      return cache.addAll(PRECACHE_URLS).catch(function () { /* ignora si falta alguno */ });
    })
  );
  /* Activa de inmediato la versión nueva, sin esperar a cerrar pestañas. */
  self.skipWaiting();
});

/* ---------- ACTIVACIÓN: borra las cachés viejas ---------- */
self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.map(function (key) {
          if (key !== CACHE_VERSION) { return caches.delete(key); }
        })
      );
    }).then(function () {
      /* Toma control de las pestañas abiertas sin recargar manualmente. */
      return self.clients.claim();
    })
  );
});

/* ---------- FETCH: decide cómo responder cada petición ---------- */
self.addEventListener('fetch', function (event) {
  const req = event.request;

  /* Solo manejamos GET; lo demás (POST al chatbot, etc.) pasa directo. */
  if (req.method !== 'GET') { return; }

  const url = new URL(req.url);

  /* No cacheamos llamadas a otros dominios (Firebase, Apps Script,
     Google Fonts/APIs, Kyte, etc.): dejamos que vayan directo a la red. */
  if (url.origin !== self.location.origin) { return; }

  /* ¿Es una navegación de página (abrir / recargar el sitio)? */
  const esNavegacion = req.mode === 'navigate' ||
    (req.headers.get('accept') || '').indexOf('text/html') !== -1;

  if (esNavegacion) {
    /* RED PRIMERO: trae siempre la versión nueva del index.html. */
    event.respondWith(
      fetch(req).then(function (resp) {
        const copia = resp.clone();
        caches.open(CACHE_VERSION).then(function (cache) { cache.put('./index.html', copia); });
        return resp;
      }).catch(function () {
        /* Sin internet: usa la última versión guardada. */
        return caches.match('./index.html').then(function (c) { return c || caches.match('./'); });
      })
    );
    return;
  }

  /* RECURSOS (css/js/imágenes del mismo sitio): STALE-WHILE-REVALIDATE. */
  event.respondWith(
    caches.match(req).then(function (cacheada) {
      const red = fetch(req).then(function (resp) {
        if (resp && resp.status === 200) {
          const copia = resp.clone();
          caches.open(CACHE_VERSION).then(function (cache) { cache.put(req, copia); });
        }
        return resp;
      }).catch(function () { return cacheada; });
      return cacheada || red;
    })
  );
});

/* ---------- Permite forzar la actualización desde la página ---------- */
self.addEventListener('message', function (event) {
  if (event.data === 'SKIP_WAITING') { self.skipWaiting(); }
});
