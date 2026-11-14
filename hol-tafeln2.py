# -*- coding: utf-8 -*-
"""
Zweiter Durchgang für die Tafeln, die hol-tafeln.py nicht bestätigen konnte.

Ältere Köhler-Dateien heißen nur "Koeh-283.jpg" — im Namen steht keine Art.
Für die gilt ein anderer, ebenso harter Nachweis: Die Datei muss in der
Commons-Kategorie "<Art> - botanical illustrations" liegen. Dort einsortiert
wird von Hand, und die Kategorie nennt die Art eindeutig.

Zusätzlich werden drei Tafeln ersetzt, die im ersten Lauf zwar den Namenstest
bestanden, aber offensichtlich nicht die Tafel zeigen (Textseite, Ausschnitt).

Aufruf:  python hol-tafeln2.py
"""

import io, json, os, re, time, urllib.error, urllib.parse, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, 'docs', 'bilder')
BERICHT = os.path.join(HIER, 'tafeln-bericht2.txt')
KOPF = {'User-Agent': 'Denkstube/1.0 (Lernprojekt; https://github.com/JokerRoyal/Denkstube)'}
PAUSE = 1.1
BREITE = 420
MINDESTGROESSE = 20000     # alles darunter ist kein Tafelbild

# Droge -> (Art, Dateiname, fester Dateititel falls schon bekannt)
NACHZUHOLEN = [
    ('Kamillenblüten',       'Matricaria recutita', 'kamille',
     'File:Matricaria recutita - Köhler–s Medizinal-Pflanzen-091.jpg'),
    ('Schafgarbenkraut',     'Achillea millefolium', 'schafgarbe',
     'File:Achillea millefolium (Köhler–s Medizinal-Pflanzen Bd.1 1887, BHL-303704, Tafel 70) clean.jpg'),
    ('Weißdornblätter mit Blüten', 'Crataegus oxyacantha', 'weissdorn', ''),
    ('Hagebuttenfrüchte',    'Rosa canina',         'hagebutte', ''),
    ('Heidelbeeren',         'Vaccinium myrtillus', 'heidelbeere', ''),
    ('Brennnesselkraut',     'Urtica dioica',       'brennnessel', ''),
    ('Schachtelhalmkraut',   'Equisetum arvense',   'schachtelhalm', ''),
    ('Spitzwegerichkraut',   'Plantago lanceolata', 'spitzwegerich', ''),
    ('Eichenrinde',          'Quercus petraea',     'eiche', ''),
    ('Flohsamen',            'Plantago psyllium',   'flohsamen', ''),
    ('Kürbissamen',          'Cucurbita pepo',      'kuerbis', ''),
    ('Primelwurzel',         'Primula veris',       'primel', ''),
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


def kategorie_dateien(kategorie):
    d = api({'action': 'query', 'list': 'categorymembers', 'cmtype': 'file',
             'cmlimit': '300', 'cmtitle': 'Category:' + kategorie})
    return [m['title'] for m in d.get('query', {}).get('categorymembers', [])]


def bild_url(titel):
    d = api({'action': 'query', 'prop': 'imageinfo', 'iiprop': 'url|size',
             'iiurlwidth': str(BREITE), 'titles': titel})
    for s in d.get('query', {}).get('pages', {}).values():
        info = (s.get('imageinfo') or [None])[0]
        if info:
            return info.get('thumburl') or info.get('url')
    return None


def main():
    zeilen = ['Zweiter Durchgang — Nachweis über die Bildkategorie der Art', '']
    treffer = json.load(io.open(os.path.join(HIER, 'tafeln.json'), encoding='utf-8'))
    for droge, art, datei, fest in NACHZUHOLEN:
        zeile = '%-28s %-22s ' % (droge, art)
        try:
            titel, grund = fest, 'fester Dateiname (vorher geprüft)'
            if not titel:
                for kat in (art + ' - botanical illustrations', art):
                    dateien = [d for d in kategorie_dateien(kat)
                               if re.search(r'köhler|koehler|koeh-', d, re.I)]
                    if dateien:
                        titel = sorted(dateien, key=len)[0]
                        grund = 'liegt in Kategorie "%s"' % kat
                        break
            if not titel:
                zeilen.append(zeile + 'OHNE BILD: keine Köhler-Datei in der Bildkategorie')
                continue
            quelle = bild_url(titel)
            if not quelle:
                zeilen.append(zeile + 'OHNE BILD: keine Bilddatei')
                continue
            rohdaten = hole(quelle)
            if len(rohdaten) < MINDESTGROESSE:
                zeilen.append(zeile + 'VERWORFEN: nur %d Bytes — kein Tafelbild' % len(rohdaten))
                continue
            with open(os.path.join(ZIEL, datei + '.jpg'), 'wb') as f:
                f.write(rohdaten)
            treffer[droge] = datei + '.jpg'
            zeilen.append(zeile + 'OK %6d B  %s  (%s)' % (
                len(rohdaten), titel.replace('File:', '')[:62], grund))
        except Exception as e:
            zeilen.append(zeile + 'FEHLER: ' + str(e)[:70])
    zeilen.append('')
    zeilen.append('jetzt %d Tafeln insgesamt' % len(treffer))
    io.open(BERICHT, 'w', encoding='utf-8').write('\n'.join(zeilen) + '\n')
    io.open(os.path.join(HIER, 'tafeln.json'), 'w', encoding='utf-8').write(
        json.dumps(treffer, ensure_ascii=False, indent=1))
    print('\n'.join(zeilen))


if __name__ == '__main__':
    main()
