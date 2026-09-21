/* Die Denkstube — Service Worker.
   Kern der App wird beim ersten Öffnen abgelegt, danach zuerst aus dem Gerät
   beantwortet. Schriften und alles Weitere wandern beim ersten Gebrauch dazu. */
const CACHE = 'denkstube-v12';
const KERN = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await Promise.all(KERN.map(u => c.add(new Request(u, {cache:'reload'})).catch(() => {})));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const namen = await caches.keys();
    await Promise.all(namen.filter(n => n !== CACHE).map(n => caches.delete(n)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const anfrage = e.request;
  if(anfrage.method !== 'GET') return;
  e.respondWith((async () => {
    /* Die Seite selbst zuerst aus dem Netz holen, damit eine neue Fassung
       sofort ankommt — ohne Netz sofort aus dem Geraet. Alles andere
       (Symbole, Schriften) bleibt umgekehrt: erst Geraet, dann Netz. */
    if(anfrage.mode === 'navigate'){
      try{
        /* cache:'reload' geht am Browser- und am GitHub-Zwischenspeicher vorbei —
           sonst bekommt man bis zu zehn Minuten lang die alte Seite. */
        const frisch = await fetch(anfrage.url, {cache:'reload'});
        if(frisch && frisch.ok){
          const c = await caches.open(CACHE);
          c.put('./index.html', frisch.clone()).catch(() => {});
          return frisch;
        }
      }catch(err){ /* offline: unten weiter */ }
    }
    const treffer = await caches.match(anfrage, {ignoreSearch:true});
    if(treffer) return treffer;
    try{
      const antwort = await fetch(anfrage);
      if(antwort && (antwort.ok || antwort.type === 'opaque')){
        const c = await caches.open(CACHE);
        c.put(anfrage, antwort.clone()).catch(() => {});
      }
      return antwort;
    }catch(err){
      if(anfrage.mode === 'navigate'){
        const start = await caches.match('./index.html');
        if(start) return start;
      }
      return new Response('', {status:504, statusText:'offline'});
    }
  })());
});
