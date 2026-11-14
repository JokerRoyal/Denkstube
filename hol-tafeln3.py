# -*- coding: utf-8 -*-
"""
Dritter Durchgang: Arten, die Köhler nicht enthält.

Für sie werden die Tafeln aus Thomés "Flora von Deutschland, Österreich und
der Schweiz" (1885) genommen — ebenfalls gemeinfrei und botanisch sauber.
Die Dateien auf Commons heißen "Illustration <Gattung> <Art>N.jpg", der
Artname steht also im Dateinamen und ist genauso hart prüfbar wie bei Köhler.

Geprüft wird doppelt: Dateiname nennt Gattung und Artwort, und die Datei muss
mindestens 20 KB groß sein (sonst ist es ein Ausschnitt, keine Tafel).

Aufruf:  python hol-tafeln3.py
"""

import io, json, os, re, time, urllib.error, urllib.parse, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, 'docs', 'bilder')
BERICHT = os.path.join(HIER, 'tafeln-bericht3.txt')
KOPF = {'User-Agent': 'Denkstube/1.0 (Lernprojekt; https://github.com/JokerRoyal/Denkstube)'}
PAUSE = 1.1
BREITE = 420
MINDESTGROESSE = 20000

OFFEN = [
    ('Birkenblätter',             'Betula pendula',      'birke'),
    ('Weißdornblätter mit Blüten','Crataegus monogyna',  'weissdorn'),
    ('Hagebuttenfrüchte',         'Rosa canina',         'hagebutte'),
    ('Heidelbeeren',              'Vaccinium myrtillus', 'heidelbeere'),
    ('Brennnesselkraut',          'Urtica dioica',       'brennnessel'),
    ('Schachtelhalmkraut',        'Equisetum arvense',   'schachtelhalm'),
    ('Spitzwegerichkraut',        'Plantago lanceolata', 'spitzwegerich'),
    ('Flohsamen',                 'Plantago afra',       'flohsamen'),
    ('Kürbissamen',               'Cucurbita pepo',      'kuerbis'),
    ('Primelwurzel',              'Primula veris',       'primel'),
    ('Schafgarbenkraut',          'Achillea millefolium','schafgarbe'),
]

_letzte = [0.0]


def hole(url):
    for versuch in range(4):
        warten = PAUSE - (time.time() - _letzte[0])
        if warten > 0:
            time.sleep(warten)
        _letzte[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=KOPF), timeout=40) as a:
                return a.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and versuch < 3:
                time.sleep(5 * (versuch + 1))
                continue
            raise


def api(params):
    return json.loads(hole('https://commons.wikimedia.org/w/api.php?format=json&'
                           + urllib.parse.urlencode(params)).decode('utf-8'))


def suche(begriff, limit=10):
    d = api({'action': 'query', 'list': 'search', 'srnamespace': '6',
             'srlimit': str(limit), 'srsearch': begriff})
    return [t['title'] for t in d.get('query', {}).get('search', [])]


def praefix_dateien(praefix):
    """Dateien, deren Name mit dem Praefix beginnt — exakt statt Volltextsuche."""
    d = api({'action': 'query', 'list': 'allimages', 'aiprefix': praefix, 'ailimit': '20'})
    return ['File:' + b['name'].replace('_', ' ') for b in d.get('query', {}).get('allimages', [])]


def bild_url(titel):
    d = api({'action': 'query', 'prop': 'imageinfo', 'iiprop': 'url|size',
             'iiurlwidth': str(BREITE), 'titles': titel})
    for s in d.get('query', {}).get('pages', {}).values():
        info = (s.get('imageinfo') or [None])[0]
        if info:
            return info.get('thumburl') or info.get('url')
    return None


def nennt_art(name, art):
    n = name.lower()
    return all(t in n for t in art.lower().split())


def main():
    zeilen = ['Dritter Durchgang — Thomé, Flora von Deutschland (1885), gemeinfrei',
              'Regel: Dateiname nennt Gattung und Artwort, Datei mindestens 20 KB.', '']
    treffer = json.load(io.open(os.path.join(HIER, 'tafeln.json'), encoding='utf-8'))
    quellen = {}
    quellpfad = os.path.join(HIER, 'tafeln-quellen.json')
    if os.path.exists(quellpfad):
        quellen = json.load(io.open(quellpfad, encoding='utf-8'))
    for droge, art, datei in OFFEN:
        zeile = '%-28s %-22s ' % (droge, art)
        try:
            kandidaten = praefix_dateien('Illustration ' + art)
            if not kandidaten:
                kandidaten = praefix_dateien(art + ' - ')
            # die "clean"-Fassungen sind freigestellt und machen sich auf der Karte besser
            kandidaten.sort(key=lambda t: (0 if 'clean' in t.lower() else 1, len(t)))
            passend = [t for t in kandidaten if nennt_art(t.replace('File:', ''), art)]
            if not passend:
                zeilen.append(zeile + 'OHNE BILD: nichts gefunden, das die Art im Namen nennt')
                continue
            genommen = None
            for titel in passend:
                quelle = bild_url(titel)
                if not quelle:
                    continue
                rohdaten = hole(quelle)
                if len(rohdaten) < MINDESTGROESSE:
                    zeilen.append(zeile + 'uebersprungen (%d B): %s' % (len(rohdaten), titel.replace('File:', '')[:50]))
                    continue
                genommen = (titel, rohdaten)
                break
            if not genommen:
                zeilen.append(zeile + 'OHNE BILD: alle Treffer zu klein')
                continue
            titel, rohdaten = genommen
            with open(os.path.join(ZIEL, datei + '.jpg'), 'wb') as f:
                f.write(rohdaten)
            treffer[droge] = datei + '.jpg'
            quellen[datei + '.jpg'] = 'thome'
            zeilen.append(zeile + 'OK %6d B  %s' % (len(rohdaten), titel.replace('File:', '')[:60]))
        except Exception as e:
            zeilen.append(zeile + 'FEHLER: ' + str(e)[:70])
    zeilen.append('')
    zeilen.append('jetzt %d Tafeln insgesamt' % len(treffer))
    io.open(BERICHT, 'w', encoding='utf-8').write('\n'.join(zeilen) + '\n')
    io.open(os.path.join(HIER, 'tafeln.json'), 'w', encoding='utf-8').write(
        json.dumps(treffer, ensure_ascii=False, indent=1))
    io.open(quellpfad, 'w', encoding='utf-8').write(json.dumps(quellen, ensure_ascii=False, indent=1))
    print('\n'.join(zeilen))


if __name__ == '__main__':
    main()
