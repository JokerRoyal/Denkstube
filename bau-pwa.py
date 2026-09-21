# -*- coding: utf-8 -*-
"""
Baut aus der Quelldatei `der-merkweg.html` das Offline-Paket:

    docs/index.html            die App als vollständige Seite
    docs/manifest.webmanifest  damit sie sich aufs Handy installieren lässt
    docs/sw.js                 der Service Worker: legt alles im Gerät ab
    docs/icon-192.png          Symbol für den Startbildschirm
    docs/icon-512.png
    Die-Denkstube-offline.html dieselbe App als einzelne Datei zum Verschicken
    Denkstube-pwa.zip          derselbe Ordner gezippt (für Netlify Drop)

`docs/` heißt so, weil GitHub Pages genau diesen Ordner ohne Umwege ausliefern
kann — die Adresse bleibt dann kurz: …github.io/denkstube/

Die Quelldatei ist für die Artifact-Umgebung geschrieben (ohne <html>, <head>,
<body> — das ergänzt die Plattform). Hier wird genau dieses Gerüst nachgebaut.

Aufruf:  python bau-pwa.py
"""

import io, os, re, shutil, struct, zlib, math, zipfile

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, 'der-merkweg.html')
ZIEL = os.path.join(HIER, 'docs')
VERSION = '11'          # bei jeder Änderung hochzählen: erneuert den Cache im Gerät

# ---------------------------------------------------------------- PNG-Symbole

def png_schreiben(pfad, breite, hoehe, pixel):
    """Schreibt RGBA-Pixel (Liste von Bytes-Zeilen) als PNG — ohne Fremdpakete."""
    rohdaten = b''.join(b'\x00' + zeile for zeile in pixel)
    def bloecke(typ, daten):
        return (struct.pack('>I', len(daten)) + typ + daten +
                struct.pack('>I', zlib.crc32(typ + daten) & 0xffffffff))
    kopf = struct.pack('>IIBBBBB', breite, hoehe, 8, 6, 0, 0, 0)
    with open(pfad, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(bloecke(b'IHDR', kopf))
        f.write(bloecke(b'IDAT', zlib.compress(rohdaten, 9)))
        f.write(bloecke(b'IEND', b''))

def symbol(groesse):
    """Eine Honigblüte auf Gartengrün. Die Blüte bleibt in der Mitte, damit
    Android das Symbol beschneiden darf (maskable) ohne etwas abzuschneiden."""
    grund   = (63, 107, 70)     # Moosgrün
    blatt   = (122, 165, 106)   # helleres Grün für zwei Blätter
    blueten = (232, 178, 74)    # Honig
    mitte   = (247, 239, 216)   # Creme
    s = groesse
    mx = my = s / 2.0
    R  = s * 0.175              # Abstand der Blütenblätter von der Mitte
    pa, pb = s * 0.110, s * 0.170   # Halbachsen eines Blütenblatts
    # Blüte + Blätter bleiben im inneren 80%-Kreis (maskable safe zone)
    winkel = [(-90 + i * 72) * math.pi / 180 for i in range(5)]
    blaetter = [   # (Mittelpunkt, Halbachsen, Drehung) für zwei Blätter am Stiel
        ((mx - s * 0.115, my + s * 0.250), (s * 0.100, s * 0.046), -0.5),
        ((mx + s * 0.115, my + s * 0.262), (s * 0.092, s * 0.042),  0.5),
    ]
    def in_ellipse(x, y, cx, cy, a, b, dreh):
        dx, dy = x - cx, y - cy
        c, si = math.cos(-dreh), math.sin(-dreh)
        rx, ry = dx * c - dy * si, dx * si + dy * c
        return (rx / a) ** 2 + (ry / b) ** 2 <= 1.0
    def farbe_an(x, y):
        # Stiel
        if abs(x - mx) <= s * 0.020 and my + s * 0.09 <= y <= my + s * 0.30:
            return blatt
        for (cx, cy), (a, b), d in blaetter:
            if in_ellipse(x, y, cx, cy, a, b, d):
                return blatt
        if (x - mx) ** 2 + (y - my) ** 2 <= (s * 0.082) ** 2:
            return mitte
        for w in winkel:
            cx, cy = mx + math.cos(w) * R, my + math.sin(w) * R
            if in_ellipse(x, y, cx, cy, pa, pb, w + math.pi / 2):
                return blueten
        return None
    zeilen = []
    hilfe = [0.25, 0.75]        # 2x2-Überabtastung für weiche Kanten
    for py in range(s):
        zeile = bytearray()
        for px in range(s):
            summe = {}
            for oy in hilfe:
                for ox in hilfe:
                    f = farbe_an(px + ox, py + oy) or grund
                    summe[f] = summe.get(f, 0) + 1
            r = g = b = 0
            for f, n in summe.items():
                r += f[0] * n; g += f[1] * n; b += f[2] * n
            zeile += bytes((r // 4, g // 4, b // 4, 255))
        zeilen.append(bytes(zeile))
    return zeilen

# ---------------------------------------------------------------- Die Seite

KOPF = '''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#eaeee2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1a1f17" media="(prefers-color-scheme: dark)">
<meta name="description" content="Gedächtnistraining in hundert Stationen — ruhig, bunt, ohne Internet.">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Denkstube">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-192.png">
<link rel="icon" href="icon-192.png">
<style>
/* Das Gerüst, das die Artifact-Umgebung sonst selbst mitbringt */
:root{
  color-scheme:light dark;
  padding-top:env(safe-area-inset-top, 0px);
  padding-bottom:env(safe-area-inset-bottom, 0px);
}
body{margin:0;}
img{max-width:100%;}
[hidden]{display:none !important;}
html{-webkit-tap-highlight-color:transparent; overscroll-behavior-y:contain;}
</style>
'''

FUSS = '''
<script>
/* Der Service Worker legt die App im Gerät ab — danach geht alles ohne Netz.
   Auf einer einzelnen Datei (file://) gibt es ihn nicht; dann läuft die App
   trotzdem, sie merkt sich den Fortschritt nur über den Browser-Speicher. */
if('serviceWorker' in navigator && location.protocol.indexOf('http') === 0){
  window.addEventListener('load', function(){
    navigator.serviceWorker.register('sw.js').catch(function(){ /* dann eben online */ });
  });
}
</script>
</body>
</html>
'''

MANIFEST = '''{
  "name": "Die Denkstube",
  "short_name": "Denkstube",
  "description": "Gedächtnistraining in hundert Stationen — ruhig, bunt, ohne Internet.",
  "lang": "de",
  "dir": "ltr",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#eaeee2",
  "theme_color": "#eaeee2",
  "categories": ["games", "health", "education"],
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
'''

SW = '''/* Die Denkstube — Service Worker.
   Kern der App wird beim ersten Öffnen abgelegt, danach zuerst aus dem Gerät
   beantwortet. Schriften und alles Weitere wandern beim ersten Gebrauch dazu. */
const CACHE = 'denkstube-v%VERSION%';
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
'''

def bauen():
    quelle = io.open(QUELLE, encoding='utf-8').read()
    schnitt = quelle.index('</style>') + len('</style>')
    kopfteil, koerper = quelle[:schnitt], quelle[schnitt:]
    seite = KOPF + kopfteil + '\n</head>\n<body>\n' + koerper.strip() + FUSS

    os.makedirs(ZIEL, exist_ok=True)
    io.open(os.path.join(ZIEL, 'index.html'), 'w', encoding='utf-8').write(seite)
    io.open(os.path.join(ZIEL, 'manifest.webmanifest'), 'w', encoding='utf-8').write(MANIFEST)
    io.open(os.path.join(ZIEL, 'sw.js'), 'w', encoding='utf-8').write(SW.replace('%VERSION%', VERSION))
    for g in (192, 512):
        png_schreiben(os.path.join(ZIEL, 'icon-%d.png' % g), g, g, symbol(g))

    # dieselbe App als einzelne Datei — zum Verschicken per Mail oder Messenger
    einzel = seite.replace('<link rel="manifest" href="manifest.webmanifest">\n', '')
    einzel = einzel.replace('<link rel="apple-touch-icon" href="icon-192.png">\n', '')
    einzel = einzel.replace('<link rel="icon" href="icon-192.png">\n', '')
    io.open(os.path.join(HIER, 'Die-Denkstube-offline.html'), 'w', encoding='utf-8').write(einzel)

    # derselbe Ordner als Zip — für Netlify Drop, wo man einen Ordner hinzieht
    zipname = os.path.join(HIER, 'Denkstube-pwa.zip')
    with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(os.listdir(ZIEL)):
            z.write(os.path.join(ZIEL, name), name)

    print('Paket gebaut:')
    for d in sorted(os.listdir(ZIEL)):
        print('  docs/%-23s %7d Bytes' % (d, os.path.getsize(os.path.join(ZIEL, d))))
    print('  %-28s %7d Bytes' % ('Denkstube-pwa.zip', os.path.getsize(zipname)))
    print('  %-28s %7d Bytes' % ('Die-Denkstube-offline.html',
                                 os.path.getsize(os.path.join(HIER, 'Die-Denkstube-offline.html'))))

if __name__ == '__main__':
    bauen()
