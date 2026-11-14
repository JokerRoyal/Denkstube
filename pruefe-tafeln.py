# -*- coding: utf-8 -*-
"""
Prüft jede geholte Tafel einzeln nach: Welche Datei ist es, welche Lizenz hat
sie, und wie heißt der Urheber? Alles, was nicht gemeinfrei ist, fliegt raus —
in der App steht schließlich "gemeinfrei" darunter.

Das Ergebnis landet in tafeln-quellen.json (für die App) und in
tafeln-nachweis.txt (zum Nachlesen).

Aufruf:  python pruefe-tafeln.py
"""

import io, json, os, re, time, urllib.error, urllib.parse, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, 'docs', 'bilder')
KOPF = {'User-Agent': 'Denkstube/1.0 (Lernprojekt; https://github.com/JokerRoyal/Denkstube)'}
PAUSE = 1.1
_letzte = [0.0]

# Droge -> Dateiname in docs/bilder
TAFELN = json.load(io.open(os.path.join(HIER, 'tafeln.json'), encoding='utf-8'))


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


def quelldateien():
    """Welche Commons-Datei steckt hinter welcher Droge? Steht in den Berichten."""
    zuordnung = {}
    for bericht in ('tafeln-bericht.txt', 'tafeln-bericht2.txt', 'tafeln-bericht3.txt'):
        pfad = os.path.join(HIER, bericht)
        if not os.path.exists(pfad):
            continue
        for zeile in io.open(pfad, encoding='utf-8'):
            m = re.match(r'^(.{1,30}?)\s{2,}\S.*?\bOK\s+\d+\s+B\s+(.+?)(?:\s+\(|\s*$)', zeile)
            if m:
                zuordnung[m.group(1).strip()] = m.group(2).strip()
    return zuordnung


def lizenz(dateititel):
    d = api({'action': 'query', 'prop': 'imageinfo', 'iiprop': 'extmetadata',
             'titles': 'File:' + dateititel})
    for s in d.get('query', {}).get('pages', {}).values():
        info = (s.get('imageinfo') or [None])[0]
        if not info:
            return None
        meta = info.get('extmetadata', {})

        def feld(name):
            w = meta.get(name, {}).get('value', '')
            return re.sub('<[^>]+>', '', w).strip()
        return {'lizenz': feld('LicenseShortName'), 'urheber': feld('Artist')[:60],
                'quelle': feld('Credit')[:60]}
    return None


def main():
    zuordnung = quelldateien()
    zeilen = ['Nachweis für jede Tafel in der Kräuterkammer', '']
    quellen = {}
    raus = []
    for droge, datei in sorted(TAFELN.items()):
        titel = zuordnung.get(droge, '')
        if not titel:
            zeilen.append('%-28s KEIN NACHWEIS — fliegt raus' % droge)
            raus.append((droge, datei))
            continue
        try:
            d = lizenz(titel) or {}
        except Exception as e:
            zeilen.append('%-28s FEHLER %s' % (droge, str(e)[:40]))
            continue
        lz = (d.get('lizenz') or '').lower()
        frei = ('public domain' in lz or lz.startswith('pd') or 'cc0' in lz
                or 'gemeinfrei' in lz or lz == '')
        werk = 'koehler' if re.search(r'köhler|koehler|koeh-', titel, re.I) else 'alt'
        if not frei:
            zeilen.append('%-28s RAUS (%s): %s' % (droge, d.get('lizenz'), titel[:50]))
            raus.append((droge, datei))
            continue
        if not re.search(r'köhler|koehler|koeh-|illustration|flora|billeder', titel, re.I):
            zeilen.append('%-28s RAUS (keine historische Tafel): %s' % (droge, titel[:50]))
            raus.append((droge, datei))
            continue
        quellen[datei] = werk
        zeilen.append('%-28s OK  %-12s %-46s %s' % (droge, d.get('lizenz'), titel[:46], (d.get('urheber') or '')[:28]))
    for droge, datei in raus:
        pfad = os.path.join(ZIEL, datei)
        if os.path.exists(pfad):
            os.remove(pfad)
        TAFELN.pop(droge, None)
    zeilen.append('')
    zeilen.append('%d Tafeln bleiben, %d entfernt' % (len(TAFELN), len(raus)))
    io.open(os.path.join(HIER, 'tafeln-nachweis.txt'), 'w', encoding='utf-8').write('\n'.join(zeilen) + '\n')
    io.open(os.path.join(HIER, 'tafeln.json'), 'w', encoding='utf-8').write(
        json.dumps(TAFELN, ensure_ascii=False, indent=1))
    io.open(os.path.join(HIER, 'tafeln-quellen.json'), 'w', encoding='utf-8').write(
        json.dumps(quellen, ensure_ascii=False, indent=1))
    print('\n'.join(zeilen))


if __name__ == '__main__':
    main()
