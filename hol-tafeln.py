# -*- coding: utf-8 -*-
"""
Holt die Pflanzentafeln aus Köhler's Medizinal-Pflanzen (1883–1914, gemeinfrei)
für die Kräuterkammer und legt sie in docs/bilder/ ab.

Warum es so umständlich ist: Eine falsche Tafel wäre schlimmer als gar keine —
dann lernt sie die falsche Pflanze. Deshalb:

  1. Zu jeder Droge steht hier die botanische Art, dazu der historische Name,
     den Köhler benutzt hat (die Tafeln sind danach benannt).
  2. Gesucht wird auf Wikimedia Commons nach "Koehler <Art>".
  3. Genommen wird nur eine Datei, deren **Dateiname beides enthält**:
     Gattung samt Artwort und einen Hinweis auf Köhler.
  4. Der vollständige Dateiname steht im Bericht — dort ist die Art ablesbar,
     sodass sich jede Zeile einzeln nachprüfen lässt.
  5. Zum Schluss wird jede Tafel noch mit eigenen Augen angesehen.

Was durchfällt, bekommt kein Bild; in der App bleibt dann das Gruppensymbol.

Aufruf:  python hol-tafeln.py
"""

import io, json, os, re, time, urllib.error, urllib.parse, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, 'docs', 'bilder')
BERICHT = os.path.join(HIER, 'tafeln-bericht.txt')
KOPF = {'User-Agent': 'Denkstube/1.0 (Lernprojekt; https://github.com/JokerRoyal/Denkstube)'}
PAUSE = 1.1
VERSUCHE = 4
BREITE = 420          # Handybreite; mehr braucht die Karte nicht

# Droge -> (Art heute, Name bei Köhler oder leer, Dateiname)
PFLANZEN = [
    ('Bärentraubenblätter',       'Arctostaphylos uva-ursi', '',                       'baerentraube'),
    ('Birkenblätter',             'Betula pendula',          'Betula alba',            'birke'),
    ('Melissenblätter',           'Melissa officinalis',     '',                       'melisse'),
    ('Pfefferminzblätter',        'Mentha piperita',         '',                       'pfefferminze'),
    ('Rosmarinblätter',           'Rosmarinus officinalis',  '',                       'rosmarin'),
    ('Salbeiblätter',             'Salvia officinalis',      '',                       'salbei'),
    ('Weißdornblätter mit Blüten','Crataegus monogyna',      'Crataegus oxyacantha',   'weissdorn'),
    ('Arnikablüten',              'Arnica montana',          '',                       'arnika'),
    ('Gewürznelken',              'Syzygium aromaticum',     'Eugenia caryophyllata',  'gewuerznelke'),
    ('Holunderblüten',            'Sambucus nigra',          '',                       'holunder'),
    ('Hopfenzapfen',              'Humulus lupulus',         '',                       'hopfen'),
    ('Kamillenblüten',            'Matricaria chamomilla',   'Matricaria recutita',    'kamille'),
    ('Lavendelblüten',            'Lavandula angustifolia',  'Lavandula officinalis',  'lavendel'),
    ('Lindenblüten',              'Tilia cordata',           'Tilia platyphyllos',     'linde'),
    ('Malvenblüten',              'Malva sylvestris',        '',                       'malve'),
    ('Ringelblumenblüten',        'Calendula officinalis',   '',                       'ringelblume'),
    ('Anisfrüchte',               'Pimpinella anisum',       '',                       'anis'),
    ('Fenchelfrüchte',            'Foeniculum vulgare',      'Foeniculum capillaceum', 'fenchel'),
    ('Hagebuttenfrüchte',         'Rosa canina',             '',                       'hagebutte'),
    ('Heidelbeeren',              'Vaccinium myrtillus',     '',                       'heidelbeere'),
    ('Kümmelfrüchte',             'Carum carvi',             '',                       'kuemmel'),
    ('Wacholderbeeren',           'Juniperus communis',      '',                       'wacholder'),
    ('Brennnesselkraut',          'Urtica dioica',           '',                       'brennnessel'),
    ('Löwenzahnwurzel mit Kraut', 'Taraxacum officinale',    '',                       'loewenzahn'),
    ('Mistelkraut',               'Viscum album',            '',                       'mistel'),
    ('Schachtelhalmkraut',        'Equisetum arvense',       '',                       'schachtelhalm'),
    ('Schafgarbenkraut',          'Achillea millefolium',    '',                       'schafgarbe'),
    ('Spitzwegerichkraut',        'Plantago lanceolata',     '',                       'spitzwegerich'),
    ('Tausendgüldenkraut',        'Centaurium erythraea',    'Erythraea centaurium',   'tausendgueldenkraut'),
    ('Thymiankraut',              'Thymus vulgaris',         '',                       'thymian'),
    ('Wermutkraut',               'Artemisia absinthium',    '',                       'wermut'),
    ('Eichenrinde',               'Quercus robur',           'Quercus pedunculata',    'eiche'),
    ('Flohsamen',                 'Plantago afra',           'Plantago psyllium',      'flohsamen'),
    ('Kürbissamen',               'Cucurbita pepo',          '',                       'kuerbis'),
    ('Leinsamen',                 'Linum usitatissimum',     '',                       'lein'),
    ('Baldrianwurzel',            'Valeriana officinalis',   '',                       'baldrian'),
    ('Eibischwurzel',             'Althaea officinalis',     '',                       'eibisch'),
    ('Enzianwurzel',              'Gentiana lutea',          '',                       'enzian'),
    ('Primelwurzel',              'Primula veris',           'Primula officinalis',    'primel'),
    ('Süßholzwurzel',             'Glycyrrhiza glabra',      '',                       'suessholz'),
]

_letzte = [0.0]


def hole(url):
    for versuch in range(VERSUCHE):
        warten = PAUSE - (time.time() - _letzte[0])
        if warten > 0:
            time.sleep(warten)
        _letzte[0] = time.time()
        try:
            anfrage = urllib.request.Request(url, headers=KOPF)
            with urllib.request.urlopen(anfrage, timeout=40) as antwort:
                return antwort.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and versuch < VERSUCHE - 1:
                time.sleep(5 * (versuch + 1))
                continue
            raise


def api(params):
    url = 'https://commons.wikimedia.org/w/api.php?format=json&' + urllib.parse.urlencode(params)
    return json.loads(hole(url).decode('utf-8'))


def suche(begriff):
    d = api({'action': 'query', 'list': 'search', 'srnamespace': '6',
             'srlimit': '10', 'srsearch': begriff})
    return [t['title'] for t in d.get('query', {}).get('search', [])]


def ist_koehler(name):
    return bool(re.search(r'köhler|koehler|koeh-', name, re.I))


def passt_zur_art(name, art, altname):
    """Der Dateiname muss Gattung UND Artwort nennen."""
    n = name.lower().replace('’', "'")
    for kandidat in [art, altname]:
        if not kandidat:
            continue
        if all(t in n for t in kandidat.lower().split()):
            return kandidat
    return None


def tafel_suchen(art, altname):
    gesehen = []
    begriffe = ['Koehler ' + art, art + ' Medizinal-Pflanzen']
    if altname:
        begriffe += ['Koehler ' + altname, altname + ' Medizinal-Pflanzen']
    for begriff in begriffe:
        for titel in suche(begriff):
            name = titel.replace('File:', '')
            if name in gesehen:
                continue
            gesehen.append(name)
            if not ist_koehler(name):
                continue
            treffer = passt_zur_art(name, art, altname)
            if treffer:
                return titel, 'Dateiname nennt "%s" und Köhler' % treffer
    return None, 'keine Tafel, deren Name die Art nennt (%d Dateien angesehen)' % len(gesehen)


def bild_url(dateititel):
    d = api({'action': 'query', 'prop': 'imageinfo', 'iiprop': 'url|size',
             'iiurlwidth': str(BREITE), 'titles': dateititel})
    for s in d.get('query', {}).get('pages', {}).values():
        info = (s.get('imageinfo') or [None])[0]
        if info:
            return info.get('thumburl') or info.get('url')
    return None


def main():
    os.makedirs(ZIEL, exist_ok=True)
    zeilen = ['Pflanzentafeln für die Kräuterkammer',
              "Quelle: Köhler's Medizinal-Pflanzen (1883-1914), gemeinfrei, über Wikimedia Commons",
              'Regel: nur Dateien, deren Name die botanische Art UND Köhler nennt.',
              'Die Dateinamen unten sind zum Nachprüfen da — jede Zeile einzeln lesen.',
              '']
    treffer = {}
    for droge, art, altname, datei in PFLANZEN:
        zeile = '%-28s %-24s ' % (droge, art)
        try:
            titel, grund = tafel_suchen(art, altname)
            if not titel:
                zeilen.append(zeile + 'OHNE BILD: ' + grund)
                continue
            quelle = bild_url(titel)
            if not quelle:
                zeilen.append(zeile + 'OHNE BILD: keine Bilddatei zu ' + titel)
                continue
            rohdaten = hole(quelle)
            with open(os.path.join(ZIEL, datei + '.jpg'), 'wb') as f:
                f.write(rohdaten)
            treffer[droge] = datei + '.jpg'
            zeilen.append(zeile + 'OK %6d B  %s' % (len(rohdaten), titel.replace('File:', '')))
        except Exception as e:
            zeilen.append(zeile + 'FEHLER: ' + str(e)[:70])
    zeilen.append('')
    zeilen.append('%d von %d Tafeln geholt' % (len(treffer), len(PFLANZEN)))
    io.open(BERICHT, 'w', encoding='utf-8').write('\n'.join(zeilen) + '\n')
    io.open(os.path.join(HIER, 'tafeln.json'), 'w', encoding='utf-8').write(
        json.dumps(treffer, ensure_ascii=False, indent=1))
    print(zeilen[-1])


if __name__ == '__main__':
    main()
